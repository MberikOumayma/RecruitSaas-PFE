"""
Matching candidat ↔ offre — architecture 5 niveaux :

  1. Semantic Score      (Sentence Transformers, similarité globale CV ↔ offre)
  2. Skill Match Score   (required_skills vs skills + experience descriptions)
  3. Experience Score    (projets / stages / profondeur sémantique)
  4. LLM Reasoning Score (Llama via Groq — score_reasoning.py)
  5. Rule-Based Score    (pénalités exigences manquantes, bonus couverture)

  final_score =
    0.20 * semantic +
    0.30 * skill +
    0.15 * experience +
    0.30 * llm_reasoning +
    0.05 * rules

  + Chroma (persistance) + FAISS (classement bulk)
"""
from __future__ import annotations

import os
import re
from typing import Optional

import numpy as np

from score_reasoning import fetch_llm_reasoning_score
from summary_pipeline import (
    _get_embedder,
    _build_job_query,
    _build_evidence_corpus,
    _format_experience_text,
    build_summary_context,
    _dedupe_skills,
    _skills_match,
    _select_latest_professional_job,
)

_CHROMA_PATH = os.getenv("CHROMA_PATH", os.path.join(os.path.dirname(__file__), "chroma_db"))

_WEIGHTS_WITH_LLM = {
    "semantic": 0.20,
    "skill": 0.30,
    "experience": 0.15,
    "llm": 0.30,
    "rules": 0.05,
}

_WEIGHTS_NO_LLM = {
    "semantic": 0.25,
    "skill": 0.38,
    "experience": 0.19,
    "rules": 0.18,
}

_chroma_client = None
_candidate_collection = None
_offer_collection = None


def _get_chroma_collections():
    global _chroma_client, _candidate_collection, _offer_collection
    if _candidate_collection is not None:
        return _candidate_collection, _offer_collection
    import chromadb
    from chromadb.config import Settings

    _chroma_client = chromadb.PersistentClient(
        path=_CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False),
    )
    _candidate_collection = _chroma_client.get_or_create_collection(
        name="candidates",
        metadata={"hnsw:space": "cosine"},
    )
    _offer_collection = _chroma_client.get_or_create_collection(
        name="job_offers",
        metadata={"hnsw:space": "cosine"},
    )
    return _candidate_collection, _offer_collection


def _embed_texts(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)
    embedder = _get_embedder()
    vectors = embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return np.asarray(vectors, dtype=np.float32)


def _embed_one(text: str) -> np.ndarray:
    rows = _embed_texts([text or " "])
    return rows[0]


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    return float(np.dot(a, b))


def _round_to_5(value: float) -> int:
    return int(round(max(0, min(100, value)) / 5.0) * 5)


def build_candidate_profile(
    skills: Optional[list[str]] = None,
    experiences: Optional[list[dict]] = None,
    cv_text: Optional[str] = None,
    max_chars: int = 2500,
) -> str:
    parts: list[str] = []
    skill_list = _dedupe_skills([str(s).strip() for s in (skills or []) if str(s).strip()])
    if skill_list:
        parts.append("Skills: " + ", ".join(skill_list[:40]))
    for exp in experiences or []:
        if isinstance(exp, dict):
            line = _format_experience_text(exp)
            if line:
                parts.append(line)
    if not parts and cv_text:
        flat = re.sub(r"\s+", " ", cv_text).strip()
        parts.append(flat[:max_chars])
    text = "\n".join(parts).strip()
    return text[:max_chars] if text else " "


def build_offer_profile(
    titre: Optional[str] = None,
    description: Optional[str] = None,
    type_contrat: Optional[str] = None,
) -> str:
    return _build_job_query(titre, description, type_contrat)


# ── Niveau 1 : Semantic ───────────────────────────────────────────────────────

def _semantic_match_score(cand_emb: np.ndarray, offer_emb: np.ndarray) -> float:
    """Similarité globale CV ↔ offre (cosine 0–1)."""
    return _cosine(cand_emb, offer_emb)


# ── Domain fit (rôle / titre / séniorité — pas seulement similarité globale) ──

_SENIORITY_SENIOR = re.compile(
    r"(?i)\b(senior|sr\.?|lead|principal|staff|expert|architect|chef|responsable)\b"
)
_SENIORITY_JUNIOR = re.compile(
    r"(?i)\b(junior|jr\.?|étudiant|etudiant|student|intern|internship|stage|stagiaire|"
    r"graduate|alternance|débutant|debutant|academic|universit)\b"
)


def _offer_is_senior_level(titre_offre: Optional[str]) -> bool:
    return bool(_SENIORITY_SENIOR.search(titre_offre or ""))


def _seniority_mismatch_factor(
    titre_offre: Optional[str],
    candidate_text: str,
) -> float:
    """Pénalité uniquement si l'offre exige un profil senior et le candidat est junior/étudiant."""
    if not _offer_is_senior_level(titre_offre):
        return 1.0
    if _SENIORITY_JUNIOR.search(candidate_text or ""):
        return 0.68
    return 1.0


def _role_title_alignment_score(
    titre_offre: Optional[str],
    offer_emb: np.ndarray,
    cand_emb: np.ndarray,
    exp_list: list[dict],
) -> float:
    """
    Similarité sémantique titre d'offre ↔ rôles/projets (Sentence Transformers, pas de liste métier).
    """
    titre = (titre_offre or "").strip()
    if not titre:
        return float(_cosine(cand_emb, offer_emb))

    title_emb = _embed_one(titre)
    sims: list[float] = [_cosine(cand_emb, title_emb)]

    latest = _select_latest_professional_job(exp_list) if exp_list else None
    if latest:
        role_text = _format_experience_text(latest)
        if len(role_text) >= 8:
            sims.append(_cosine(_embed_one(role_text), title_emb))

    for exp in exp_list[:5]:
        t = _format_experience_text(exp)
        if len(t) >= 10:
            sims.append(_cosine(_embed_one(t), title_emb))

    sims.sort(reverse=True)
    if len(sims) >= 2:
        return max(sims[0], 0.50 * sims[0] + 0.50 * sims[1])
    return sims[0]


def _domain_fit_score(
    cand_emb: np.ndarray,
    offer_emb: np.ndarray,
    titre_offre: Optional[str],
    exp_list: list[dict],
    skill_score: int,
    cand_text: str,
    type_contrat: Optional[str],
) -> tuple[int, float, float]:
    """
    Domain fit 0–100 + signaux role_sim / global_sim pour calibration UI.
    Cohérence sémantique (titre↔rôle, profil↔offre) sans vocabulaire métier codé.
    """
    role_sim = _role_title_alignment_score(titre_offre, offer_emb, cand_emb, exp_list)
    global_sim = _cosine(cand_emb, offer_emb)
    skill_norm = skill_score / 100.0

    raw = 0.45 * role_sim + 0.30 * global_sim + 0.25 * skill_norm

    # Boost si titre/rôle ET profil global convergent (ex. stage ↔ profil étudiant aligné)
    if role_sim >= 0.50 and global_sim >= 0.48:
        coherent = (
            0.50 * max(role_sim, global_sim)
            + 0.30 * min(role_sim, global_sim)
            + 0.20 * skill_norm
        )
        raw = max(raw, coherent)

    raw *= _seniority_mismatch_factor(titre_offre, cand_text)

    # Plafond skills seulement si les deux signaux sémantiques sont faibles (mauvais métier)
    clear_mismatch = role_sim < 0.42 and global_sim < 0.45
    if clear_mismatch:
        raw = min(raw, skill_norm * 0.92 + 0.06)

    return _round_to_5(raw * 100), role_sim, global_sim


# ── Niveau 2 : Skill match ────────────────────────────────────────────────────

def _skill_match_score(skill_gaps: dict) -> tuple[int, list[str], list[str]]:
    """
    required vs candidate (skills + experiences): fit_score = matched / total * 100.
    Retourne (score, skills_matched_labels, skills_missing).
    """
    present = skill_gaps.get("present") or []
    missing = skill_gaps.get("missing") or []
    fit = int(skill_gaps.get("fit_score", 0))
    matched: list[str] = []
    seen: set[str] = set()
    for p in present:
        if not p:
            continue
        label = str(p.get("found_as") or p.get("required") or "").strip()
        if not label:
            continue
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        matched.append(label[:80])
    return _round_to_5(fit), matched, list(missing)


def _build_skill_summary(skill_gaps: dict) -> str:
    lines = []
    for p in skill_gaps.get("present") or []:
        lines.append(f"MATCH: {p.get('required')} → {p.get('found_as')}")
    for m in skill_gaps.get("missing") or []:
        lines.append(f"MISSING: {m}")
    reqs = skill_gaps.get("requirements_checked") or []
    if reqs:
        lines.insert(0, f"Requirements checked ({len(reqs)}): " + "; ".join(reqs[:12]))
    return "\n".join(lines) if lines else "No structured skill comparison available."


# ── Niveau 3 : Experience ─────────────────────────────────────────────────────

def _is_internship_contract(type_contrat: Optional[str]) -> bool:
    if not type_contrat:
        return False
    return bool(re.search(r"stage|intern|stagiaire|alternance", type_contrat, re.I))


def _estimate_experience_years(experiences: list[dict]) -> float:
    """Estimation grossière à partir des champs years/dates."""
    total = 0.0
    for exp in experiences:
        raw = str(exp.get("years") or exp.get("dates") or "")
        if not raw:
            continue
        years_found = re.findall(r"(20\d{2})", raw)
        if len(years_found) >= 2:
            try:
                span = int(years_found[-1]) - int(years_found[0])
                total += max(0.5, min(span, 10))
            except ValueError:
                total += 0.5
        elif years_found:
            total += 0.5
        elif re.search(r"mois|month", raw, re.I):
            total += 0.25
    return min(total, 15.0)


def _experience_semantic_score(offer_emb: np.ndarray, experiences: list[dict], cv_text: Optional[str]) -> float:
    """
    Moyenne des meilleures similarités + bonus couverture (plusieurs expériences/projets pertinents).
    """
    texts: list[str] = []
    for exp in experiences or []:
        if isinstance(exp, dict):
            t = _format_experience_text(exp)
            if len(t) >= 12:
                texts.append(t)
    if not texts and cv_text:
        flat = re.sub(r"\s+", " ", cv_text).strip()
        for part in re.split(r"(?<=[.!?])\s+", flat):
            part = part.strip()
            if len(part) >= 40:
                texts.append(part[:500])
        if not texts and flat:
            texts.append(flat[:1500])
    if not texts:
        return 0.0

    exp_embs = _embed_texts(texts)
    sims = sorted((exp_embs @ offer_emb).tolist(), reverse=True)
    k = min(5, len(sims))
    top_mean = float(np.mean(sims[:k]))

    threshold = max(0.36, sims[0] * 0.70) if sims else 0.4
    relevant_ratio = sum(1 for s in sims if s >= threshold) / len(sims)
    coverage_bonus = min(0.12, relevant_ratio * 0.10)

    overall = float(np.mean(sims))
    blended = 0.55 * top_mean + 0.30 * overall + 0.15 * float(np.median(sims))
    return min(1.0, blended + coverage_bonus)


def _experience_match_score(
    offer_emb: np.ndarray,
    experiences: list[dict],
    cv_text: Optional[str],
    type_contrat: Optional[str],
    titre_offre: Optional[str] = None,
) -> float:
    """
    Similarité sémantique + profondeur du parcours (stages, projets, alternances).
    Pour offres junior/stage : la profondeur compte davantage que les années.
    """
    sem = _experience_semantic_score(offer_emb, experiences, cv_text)
    n = len(experiences) if experiences else 0
    depth = min(1.0, n / 5.0) if n else 0.0

    years = _estimate_experience_years(experiences)
    intern_offer = _is_internship_contract(type_contrat) or not _offer_is_senior_level(titre_offre)

    if intern_offer:
        years_factor = 0.82 + min(0.18, depth * 0.18)
        raw = 0.52 * sem + 0.36 * depth + 0.12 * years_factor
        if n >= 5 and sem >= 0.45:
            raw = min(1.0, raw + 0.08)
        return raw

    years_factor = min(1.0, years / 3.0) if years > 0 else 0.35
    return 0.68 * sem + 0.22 * depth + 0.10 * years_factor


# ── Niveau 5 : Rules ──────────────────────────────────────────────────────────

_HARD_MARKERS = re.compile(
    r"(?i)\b(obligatoire|required|must|indispensable|mandatory|exigé|exige)\b"
)


def _is_hard_requirement(req: str, description: Optional[str]) -> bool:
    if _HARD_MARKERS.search(req):
        return True
    if not description:
        return False
    for line in description.splitlines():
        if req.lower() in line.lower() and _HARD_MARKERS.search(line):
            return True
    return False


def _rules_score(
    skill_gaps: dict,
    skill_list: list[str],
    experiences: list[dict],
    description: Optional[str],
) -> tuple[int, list[str]]:
    """
    Score 0–100 : base 100, −20 par exigence dure manquante, bonus si forte couverture.
    Evidence = skills + experience texts (same corpus as summary gap analysis).
    """
    score = 100.0
    penalties: list[str] = []
    missing = skill_gaps.get("missing") or []
    present = skill_gaps.get("present") or []
    requirements = skill_gaps.get("requirements_checked") or []
    corpus = _build_evidence_corpus(skill_list, experiences)

    for req in missing:
        hard = _is_hard_requirement(req, description)
        still_absent = not any(_skills_match(req, s) for s in corpus)
        if hard and still_absent:
            score -= 20
            penalties.append(f"hard_missing:{req}")
        elif still_absent and len(req) <= 35:
            score -= 10
            penalties.append(f"missing:{req}")

    if requirements:
        ratio = len(present) / max(len(requirements), 1)
        if ratio >= 0.75:
            score = min(100, score + 10)
        elif ratio >= 0.5:
            score = min(100, score + 5)

    return _round_to_5(score), penalties


# ── Agrégation finale ─────────────────────────────────────────────────────────

def compute_match_score(
    cv_text: Optional[str] = None,
    skills: Optional[list[str]] = None,
    experiences: Optional[list[dict]] = None,
    titre_offre: Optional[str] = None,
    description: Optional[str] = None,
    type_contrat: Optional[str] = None,
    candidate_id: Optional[str] = None,
    offer_id: Optional[str] = None,
    use_llm: bool = True,
) -> dict:
    skill_list = _dedupe_skills([str(s).strip() for s in (skills or []) if str(s).strip()])
    exp_list = [e for e in (experiences or []) if isinstance(e, dict)]

    cand_text = build_candidate_profile(skill_list, exp_list, cv_text)
    offer_text = build_offer_profile(titre_offre, description, type_contrat)

    cand_emb = _embed_one(cand_text)
    offer_emb = _embed_one(offer_text)

    # Niveau 1
    semantic_raw = _semantic_match_score(cand_emb, offer_emb)
    semantic_score = _round_to_5(semantic_raw * 100)

    # Niveau 2
    skill_gaps: dict = {"fit_score": 0, "present": [], "missing": [], "requirements_checked": []}
    if titre_offre or description:
        ctx = build_summary_context(
            skills=skill_list,
            experiences=exp_list,
            titre_offre=titre_offre,
            description=description,
            type_contrat=type_contrat,
        )
        skill_gaps = ctx.get("skill_gaps") or skill_gaps

    skill_score, matched_skills, missing_skills = _skill_match_score(skill_gaps)

    # Niveau 3
    exp_raw = _experience_match_score(offer_emb, exp_list, cv_text, type_contrat, titre_offre)
    experience_score = _round_to_5(exp_raw * 100)

    # Niveau 4
    llm_data: dict = {}
    llm_overall = semantic_score
    if use_llm:
        llm_data = fetch_llm_reasoning_score(
            titre_offre=titre_offre,
            description=description,
            type_contrat=type_contrat,
            candidate_profile=cand_text,
            skill_summary=_build_skill_summary(skill_gaps),
            semantic_score=semantic_score,
            skill_score=skill_score,
            experience_score=experience_score,
        )
        llm_overall = _round_to_5(llm_data.get("overall_reasoning_score", semantic_score))

    # Niveau 5
    rules_score, rule_penalties = _rules_score(skill_gaps, skill_list, exp_list, description)

    # Formule finale
    if use_llm and llm_data.get("source") == "llm":
        w = _WEIGHTS_WITH_LLM
        final_raw = (
            w["semantic"] * semantic_score
            + w["skill"] * skill_score
            + w["experience"] * experience_score
            + w["llm"] * llm_overall
            + w["rules"] * rules_score
        )
    else:
        w = _WEIGHTS_NO_LLM
        final_raw = (
            w["semantic"] * semantic_score
            + w["skill"] * skill_score
            + w["experience"] * experience_score
            + w["rules"] * rules_score
        )

    score = _round_to_5(final_raw)

    # Barres UI
    llm_tech = llm_data.get("technical_fit")
    llm_exp = llm_data.get("experience_fit")
    llm_domain = llm_data.get("domain_fit")

    domain_semantic, role_sim, global_sim = _domain_fit_score(
        cand_emb, offer_emb, titre_offre, exp_list, skill_score, cand_text, type_contrat,
    )

    technical_bar = _round_to_5((skill_score + (llm_tech or skill_score)) / 2) if llm_tech else skill_score

    if llm_exp is not None:
        experience_bar = _round_to_5(0.55 * experience_score + 0.45 * llm_exp)
    else:
        experience_bar = experience_score

    if (
        not _offer_is_senior_level(titre_offre)
        and len(exp_list) >= 5
        and experience_score >= 65
    ):
        experience_bar = max(experience_bar, experience_score)

    if llm_domain is not None:
        domain_bar = _round_to_5(0.40 * domain_semantic + 0.30 * llm_domain + 0.30 * skill_score)
    else:
        domain_bar = domain_semantic

    clear_mismatch = role_sim < 0.42 and global_sim < 0.45
    if clear_mismatch:
        domain_bar = min(domain_bar, skill_score + 10)
    elif role_sim >= 0.50 and global_sim >= 0.48 and skill_score >= 65:
        domain_bar = max(domain_bar, _round_to_5((domain_semantic + skill_score) / 2))

    _persist_vectors(
        candidate_id=candidate_id,
        offer_id=offer_id,
        cand_text=cand_text,
        offer_text=offer_text,
        cand_emb=cand_emb,
        offer_emb=offer_emb,
    )

    return {
        "score": score,
        "domain_fit": domain_bar,
        "technical": technical_bar,
        "experience": experience_bar,
        "semantic_similarity": round(semantic_raw, 3),
        "breakdown": {
            "semantic_score": semantic_score,
            "domain_semantic_score": domain_semantic,
            "skill_score": skill_score,
            "experience_score": experience_score,
            "llm_reasoning_score": llm_overall,
            "rules_score": rules_score,
            "weights": w,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "rule_penalties": rule_penalties,
            "llm": llm_data,
        },
    }


def _persist_vectors(
    candidate_id: Optional[str],
    offer_id: Optional[str],
    cand_text: str,
    offer_text: str,
    cand_emb: np.ndarray,
    offer_emb: np.ndarray,
) -> None:
    try:
        cand_coll, offer_coll = _get_chroma_collections()
        if candidate_id:
            cand_coll.upsert(
                ids=[str(candidate_id)],
                embeddings=[cand_emb.tolist()],
                documents=[cand_text[:4000]],
            )
        if offer_id:
            offer_coll.upsert(
                ids=[str(offer_id)],
                embeddings=[offer_emb.tolist()],
                documents=[offer_text[:4000]],
            )
    except Exception:
        pass


def rank_candidates_for_offer(
    titre_offre: str,
    description: Optional[str],
    candidates: list[dict],
    type_contrat: Optional[str] = None,
    top_k: Optional[int] = None,
) -> list[dict]:
    """Classement FAISS rapide ; scoring détaillé sans LLM (bulk)."""
    if not candidates:
        return []

    offer_text = build_offer_profile(titre_offre, description, type_contrat)
    offer_emb = _embed_one(offer_text)

    ids: list[str] = []
    profiles: list[str] = []
    meta: list[dict] = []

    for i, c in enumerate(candidates):
        cid = str(c.get("id") or c.get("candidatureId") or f"cand-{i}")
        skills = c.get("skills") or []
        exps = c.get("experiences") or []
        cv = c.get("texteExtrait") or c.get("cvText") or ""
        profile = build_candidate_profile(skills, exps, cv)
        ids.append(cid)
        profiles.append(profile)
        meta.append({"skills": skills, "experiences": exps, "texteExtrait": cv})

    cand_embs = _embed_texts(profiles)
    if cand_embs.shape[0] == 0:
        return []

    import faiss

    dim = cand_embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(cand_embs)

    k = len(ids) if top_k is None else min(top_k, len(ids))
    similarities, indices = index.search(offer_emb.reshape(1, -1), k)

    results: list[dict] = []
    for rank_idx, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(ids):
            continue
        cid = ids[idx]
        sim = float(similarities[0][rank_idx])
        m = meta[idx]
        detail = compute_match_score(
            cv_text=m.get("texteExtrait"),
            skills=m.get("skills"),
            experiences=m.get("experiences"),
            titre_offre=titre_offre,
            description=description,
            type_contrat=type_contrat,
            candidate_id=cid,
            use_llm=False,
        )
        detail["vector_similarity"] = round(sim, 3)
        results.append({"id": cid, **detail})

    results.sort(key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1
    return results


def search_similar_candidates(
    offer_id: str,
    n_results: int = 10,
) -> list[dict]:
    try:
        _, offer_coll = _get_chroma_collections()
        offer = offer_coll.get(ids=[str(offer_id)], include=["embeddings"])
        if not offer["embeddings"]:
            return []
        offer_emb = offer["embeddings"][0]
        cand_coll, _ = _get_chroma_collections()
        hits = cand_coll.query(
            query_embeddings=[offer_emb],
            n_results=n_results,
            include=["documents", "distances", "metadatas"],
        )
        out = []
        for i, cid in enumerate(hits["ids"][0]):
            dist = hits["distances"][0][i] if hits.get("distances") else 0
            sim = round(1 - float(dist), 3) if dist is not None else 0
            out.append({
                "id": cid,
                "similarity": sim,
                "document": (hits["documents"][0][i] or "")[:200],
            })
        return out
    except Exception:
        return []
