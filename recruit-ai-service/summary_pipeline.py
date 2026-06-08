"""
Pipeline résumé candidat (données pré-extraites uniquement) :
  1. Skills + expériences extraites (AnalyseCV)
  2. Sentence Transformers — comparaison sémantique offre ↔ candidat
  3. Matrice ✓/✗ + skills alignées + score fit % (cosine)
  4. Contexte structuré → LLM (rédaction naturelle, faits imposés)
  5. Fallback compose_summary si le LLM échoue
  NOTE: Output is ALWAYS in English regardless of CV language.
"""
from __future__ import annotations

import re
from typing import Optional

# Seuils cosine (sentence-transformers)
GAP_MATCH_THRESHOLD = 0.55
SEMANTIC_HIGH_THRESHOLD = 0.62
SKILL_MATCH_THRESHOLD = 0.58

_SECTION_WEIGHTS = {
    "experience": 1.0,
    "skills": 0.95,
}

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _embedder


_PROJECT_MARKERS = (
    "projet personnel",
    "projet académique",
    "projet academique",
    "projet perso",
    "personal project",
    "academic project",
    "side project",
    "projet étudiant",
    "projet etudiant",
    "student project",
)

_MONTH_MAP = {
    "janvier": 1, "january": 1, "jan": 1,
    "février": 2, "fevrier": 2, "february": 2, "feb": 2,
    "mars": 3, "march": 3, "mar": 3,
    "avril": 4, "april": 4, "apr": 4,
    "mai": 5, "may": 5,
    "juin": 6, "june": 6, "jun": 6,
    "juillet": 7, "july": 7, "jul": 7,
    "août": 8, "aout": 8, "august": 8, "aug": 8,
    "septembre": 9, "september": 9, "sep": 9, "sept": 9,
    "octobre": 10, "october": 10, "oct": 10,
    "novembre": 11, "november": 11, "nov": 11,
    "décembre": 12, "decembre": 12, "december": 12, "dec": 12,
}


def _strip_html(text: str) -> str:
    """Supprime toutes les balises HTML et normalise les espaces."""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"&[a-z]+;", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _is_personal_project(exp: dict) -> bool:
    role = str(exp.get("role") or "").lower().strip()
    org = str(exp.get("entreprise") or exp.get("company") or "").lower().strip()
    combined = f"{role} {org}"
    return any(marker in combined for marker in _PROJECT_MARKERS)


def _parse_years_sort_key(years: str) -> tuple[int, int]:
    raw = (years or "").strip()
    if not raw or raw.lower() in {"non spécifié", "non specifie", "n/a", "none", "-"}:
        return (0, 0)

    lower = raw.lower()
    is_ongoing = any(
        token in lower
        for token in ("présent", "present", "current", "aujourd", "now", "en cours", "ongoing")
    )

    years_found = [int(y) for y in re.findall(r"(?:19|20)\d{2}", raw)]
    end_year = max(years_found) if years_found else 0

    end_month = 0
    for name, num in _MONTH_MAP.items():
        if re.search(rf"\b{re.escape(name)}\b", lower):
            end_month = max(end_month, num)

    if is_ongoing:
        end_year = max(end_year, 9999)
        if end_month == 0:
            end_month = 12

    return (end_year, end_month)


def _select_latest_professional_job(experiences: list[dict]) -> Optional[dict]:
    if not experiences:
        return None
    professional = [e for e in experiences if not _is_personal_project(e)]
    pool = professional if professional else experiences
    return max(pool, key=lambda e: _parse_years_sort_key(str(e.get("years") or e.get("dates") or "")))


def _build_sentence1_hint(latest_job: Optional[dict]) -> Optional[str]:
    """Always builds the opening sentence in English."""
    if not latest_job:
        return None
    role = str(latest_job.get("role") or "").strip()
    org = str(latest_job.get("entreprise") or latest_job.get("company") or "").strip()
    years = str(latest_job.get("years") or latest_job.get("dates") or "").strip()

    s = f"Most recently, the candidate held the role of {role}" if role else "Most recently, the candidate held a professional role"
    if org:
        s += f" at {org}"
    if years:
        s += f" ({years})"
    return s + "."


def _normalize_skill_key(skill: str) -> str:
    s = (skill or "").lower().strip()
    s = re.sub(r"[-_\s]", "", s)
    s = re.sub(r"[^\w+#]", "", s)
    return s


_SKILL_STOPWORDS = frozenset({
    "and", "or", "the", "for", "with", "from", "using", "etc",
    "et", "ou", "le", "la", "les", "de", "du", "des", "en", "un", "une",
    "a", "an", "to", "of", "in", "on", "at", "by", "as",
})

_MAX_REQUIREMENT_WORDS = 5
_MAX_REQUIREMENT_CHARS = 45


def _strip_leading_qualifier(text: str) -> str:
    """Remove short 'X de/en/of Y' lead-ins — no fixed vocabulary."""
    prev = None
    cur = text.strip()
    pattern = re.compile(
        r"^[^\s,;:]{3,}\s+(?:de|d'|en|des|du|de la|of|in|for|with|sur|on|à|a)\s+",
        re.I,
    )
    while cur != prev:
        prev = cur
        cur = pattern.sub("", cur, count=1).strip()
    return cur


def _is_plausible_single_token(token: str) -> bool:
    t = token.strip()
    if len(t) >= 4:
        return True
    if t.isupper() and len(t) >= 2:
        return True
    return bool(re.search(r"[0-9+#./]", t))


def _is_plausible_requirement(text: str) -> bool:
    """Keep short requirement labels; drop long narrative fragments (structural rules only)."""
    cleaned = _strip_leading_qualifier(
        re.sub(r"\s+", " ", (text or "").strip().strip(" .-–—•:;,"))
    )
    if not cleaned or len(cleaned) < 2:
        return False
    if len(cleaned) > _MAX_REQUIREMENT_CHARS:
        return False
    words = cleaned.split()
    if not words or len(words) > _MAX_REQUIREMENT_WORDS:
        return False
    if re.search(r"\b(?:19|20)\d{2}\b", cleaned):
        return False
    if "(" in cleaned or ")" in cleaned:
        return False
    if len(words) == 1 and not _is_plausible_single_token(words[0]):
        return False
    content_words = [w for w in words if w.lower() not in _SKILL_STOPWORDS]
    if not content_words:
        return False
    if len(words) >= 3 and len(content_words) / len(words) < 0.5:
        return False
    return True


def _looks_like_meta_label(text: str) -> bool:
    """Section headers / noise — detected by shape, not domain words."""
    t = text.strip()
    if not t:
        return True
    if t.endswith(":") and len(t.split()) <= 4:
        return True
    return len(t.split()) == 1 and len(t) <= 3


def _clean_missing_gaps(missing: list[str], max_items: int = 6) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in missing:
        label = str(item).strip()
        if not _is_plausible_requirement(label):
            continue
        key = _normalize_skill_key(label)
        if key in seen:
            continue
        seen.add(key)
        result.append(label)
    return result[:max_items]


def _short_match_label(req: str, item: str, skills: list[str]) -> Optional[str]:
    """Prefer a short skill label over a full experience paragraph."""
    for skill in skills:
        if _skills_match(req, skill):
            return skill
    if item in skills or len(item) <= 35:
        return item
    item_key = _normalize_skill_key(item)
    for skill in skills:
        if _normalize_skill_key(skill) in item_key or item_key in _normalize_skill_key(skill):
            return skill
    for token in re.findall(r"\b[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9+#./\-]{1,}\b", item):
        if _skills_match(req, token) and _is_plausible_requirement(token):
            return token
    return None

    tokens_a = {
        t for t in re.findall(r"\b\w+\b", (a or "").lower())
        if len(t) >= min_len and t not in _SKILL_STOPWORDS
    }
    tokens_b = {
        t for t in re.findall(r"\b\w+\b", (b or "").lower())
        if len(t) >= min_len and t not in _SKILL_STOPWORDS
    }
    return bool(tokens_a & tokens_b)


def _accept_semantic_match(
    requirement: str,
    candidate: str,
    sim: float,
    match_type: str,
) -> bool:
    if match_type == "exact":
        return True
    if sim >= SEMANTIC_HIGH_THRESHOLD:
        return True
    if sim >= SKILL_MATCH_THRESHOLD and _share_significant_token(requirement, candidate):
        return True
    return False


def _build_evidence_corpus(skills: list[str], experiences: list[dict]) -> list[str]:
    corpus: list[str] = [str(s).strip() for s in skills if str(s).strip()]
    for exp in experiences or []:
        text = _format_experience_text(exp)
        if text:
            corpus.append(text)
    return corpus


def _requirement_supported(requirement: str, corpus: list[str]) -> bool:
    return any(_skills_match(requirement, item) for item in corpus if item)


def _find_skills_matching_offer(
    skills: list[str],
    requirements: list[str],
    job_query: str,
    experiences: Optional[list[dict]] = None,
    max_items: int = 8,
) -> list[str]:
    exp_list = experiences or []
    if not skills and not exp_list:
        return []

    targets = [r for r in (requirements or []) if r and r.strip() and len(r.strip()) <= 80]
    if not targets and job_query.strip():
        targets = [r for r in _extract_requirement_phrases(job_query) if len(r) <= 80]
    if not targets and job_query.strip():
        targets = [job_query.strip()[:500]]

    if not targets:
        return []

    matched: list[str] = []
    seen: set[str] = set()
    corpus = _build_evidence_corpus(skills, exp_list)

    for skill in skills:
        if any(_skills_match(req, skill) for req in targets):
            key = _normalize_skill_key(skill)
            if key not in seen:
                seen.add(key)
                matched.append(skill)

    remaining = [s for s in skills if _normalize_skill_key(s) not in seen]
    if remaining:
        embedder = _get_embedder()
        from sentence_transformers.util import cos_sim

        req_embs = embedder.encode(targets, convert_to_tensor=True)
        for skill in remaining:
            skill_emb = embedder.encode(skill, convert_to_tensor=True)
            sims = cos_sim(skill_emb, req_embs)[0].tolist()
            best_idx = max(range(len(sims)), key=lambda j: sims[j])
            best_sim = float(sims[best_idx])
            if _accept_semantic_match(targets[best_idx], skill, best_sim, "semantic"):
                key = _normalize_skill_key(skill)
                if key not in seen:
                    seen.add(key)
                    matched.append(skill)

    for req in targets:
        if any(_skills_match(req, item) for item in corpus):
            for token in re.findall(r"\b[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9+#./\-]{1,}\b", req):
                tk = _normalize_skill_key(token)
                if len(tk) < 2 or tk in _SKILL_STOPWORDS:
                    continue
                if any(tk in _normalize_skill_key(item) for item in corpus):
                    label = _short_match_label(req, next(item for item in corpus if tk in _normalize_skill_key(item)), skills)
                    if label:
                        key = _normalize_skill_key(label)
                        if key not in seen:
                            seen.add(key)
                            matched.append(label)
                    break

    return matched[:max_items]


def _share_significant_token(a: str, b: str, min_len: int = 4) -> bool:
    tokens_a = {
        t for t in re.findall(r"\b\w+\b", (a or "").lower())
        if len(t) >= min_len and t not in _SKILL_STOPWORDS
    }
    tokens_b = {
        t for t in re.findall(r"\b\w+\b", (b or "").lower())
        if len(t) >= min_len and t not in _SKILL_STOPWORDS
    }
    return bool(tokens_a & tokens_b)


def _skills_match(requirement: str, candidate: str, min_substring_len: int = 3) -> bool:
    req_key = _normalize_skill_key(requirement)
    cand_key = _normalize_skill_key(candidate)
    if not req_key or not cand_key:
        return False
    if req_key == cand_key:
        return True
    if len(req_key) >= min_substring_len and req_key in cand_key:
        return True
    if len(cand_key) >= min_substring_len and cand_key in req_key:
        return True
    for token in re.findall(r"\b[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9+#./\-]{0,}\b", requirement):
        tk = _normalize_skill_key(token)
        if len(tk) < 2 or tk in _SKILL_STOPWORDS:
            continue
        if tk in cand_key:
            return True
    return False


def _extract_offer_requirements(titre: Optional[str], description: Optional[str], max_items: int = 20) -> list[str]:
    titre_clean = _strip_html(titre or "")
    desc_clean = _strip_html(description or "")
    raw = "\n".join(p for p in [titre_clean, desc_clean] if p.strip())
    if not raw.strip():
        return []

    phrases: list[str] = []
    seen: set[str] = set()

    def _add(text: str) -> None:
        text = _strip_html(text)
        cleaned = re.sub(r"^.{1,35}:\s*", "", text.strip())
        cleaned = _strip_leading_qualifier(cleaned.strip(" .-–—•:;,"))
        if not _is_plausible_requirement(cleaned):
            return
        key = _normalize_skill_key(cleaned)
        if len(key) < 3 or key in seen:
            return
        seen.add(key)
        phrases.append(cleaned)

    for line in re.split(r"[\n\r]+", raw):
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^[-•*]\s+", "", line)
        for part in re.split(r"[,;.]|\s+(?:et|and)\s+", line, flags=re.I):
            _add(part.strip())

    for token in re.findall(r"\b[A-Z][A-Z0-9]{1,6}\b", desc_clean):
        _add(token)

    if phrases and titre_clean and _normalize_skill_key(phrases[0]) == _normalize_skill_key(titre_clean):
        phrases.pop(0)

    return phrases[:max_items]


def _requirements_section(job_query: str) -> str:
    m = re.search(r"(?:Requirements|Compétences|Competences|Skills)\s*:\s*(.+)", job_query, flags=re.I | re.S)
    if m:
        return m.group(1).strip()
    cleaned = re.sub(r"Job title\s*:\s*[^\n]+", "", job_query, flags=re.I)
    cleaned = re.sub(r"Contract\s*:\s*[^\n]+", "", cleaned, flags=re.I)
    return cleaned.strip()


def _extract_requirement_phrases(job_query: str, max_items: int = 30) -> list[str]:
    source = _strip_html(_requirements_section(job_query))
    if not source.strip():
        return []

    phrases: list[str] = []
    seen: set[str] = set()

    def _add(raw: str) -> None:
        raw = _strip_html(raw)
        cleaned = re.sub(
            r"^(?:requirements?|compétences?|competences?|skills?|technologies?|tools?)\s*:?\s*",
            "",
            raw.strip(),
            flags=re.I,
        ).strip(" .-–—")
        if not _is_plausible_requirement(cleaned):
            return
        key = _normalize_skill_key(cleaned)
        if len(key) < 2:
            return
        if key in seen:
            return
        seen.add(key)
        phrases.append(cleaned)

    for chunk in re.split(r"[,;•\n|/]|(?:\s+et\s+)|(?:\s+and\s+)", source, flags=re.I):
        _add(chunk)

    for token in re.findall(r"\b[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ0-9+#./\-]{1,}\b", source):
        _add(token)

    return phrases[:max_items]


def _find_best_match(
    requirement: str,
    corpus: list[str],
    sims: list[float],
) -> tuple[int, float, str]:
    for j, item in enumerate(corpus):
        if _skills_match(requirement, item):
            return j, 1.0, "exact"

    best_idx = max(range(len(sims)), key=lambda j: sims[j])
    return best_idx, sims[best_idx], "semantic"


def _build_offer_comparison(
    skills: list[str],
    experiences: list[dict],
    titre: Optional[str],
    description: Optional[str],
    threshold: float = GAP_MATCH_THRESHOLD,
) -> dict:
    requirements = _extract_offer_requirements(titre, description)
    exp_list = experiences or []
    corpus = _build_evidence_corpus(skills, exp_list)
    latest_job = _select_latest_professional_job(exp_list)

    if not requirements:
        return {
            "requirements_checked": [],
            "present": [],
            "missing": [],
            "comparison_lines": [],
            "fit_score": 0,
            "fit_label": "unknown",
        }

    if not corpus:
        missing = requirements
        return {
            "requirements_checked": requirements,
            "present": [],
            "missing": missing,
            "comparison_lines": [f"✗ {r} → not found" for r in missing],
            "fit_score": 0,
            "fit_label": "weak",
        }

    embedder = _get_embedder()
    from sentence_transformers.util import cos_sim

    req_embs = embedder.encode(requirements, convert_to_tensor=True)
    corpus_embs = embedder.encode(corpus, convert_to_tensor=True)
    sim_matrix = cos_sim(req_embs, corpus_embs)

    present: list[dict] = []
    missing: list[str] = []
    comparison_lines: list[str] = []

    for i, req in enumerate(requirements):
        sims = sim_matrix[i].tolist()
        best_idx, best_sim, match_type = _find_best_match(req, corpus, sims)
        evidence = corpus[best_idx][:100]

        if _accept_semantic_match(req, evidence, best_sim, match_type):
            present.append({
                "required": req,
                "found_as": evidence,
                "similarity": round(float(best_sim if match_type == "semantic" else 1.0), 3),
                "match_type": match_type,
            })
            comparison_lines.append(f"✓ OFFER: {req} → CANDIDATE: {evidence}")
        elif _requirement_supported(req, corpus):
            support = next(item for item in corpus if _skills_match(req, item))
            present.append({
                "required": req,
                "found_as": support[:100],
                "similarity": 1.0,
                "match_type": "lexical",
            })
            comparison_lines.append(f"✓ OFFER: {req} → CANDIDATE: {support[:100]}")
        else:
            missing.append(req)
            comparison_lines.append(f"✗ OFFER: {req} → CANDIDATE: not found (best_sim={round(best_sim, 2)})")

    missing = _filter_spurious_gaps(missing, present, skills, exp_list, latest_job)
    missing = _clean_missing_gaps(missing)

    comparison_lines = []
    present_reqs = {p["required"] for p in present}
    for req in requirements:
        if req in present_reqs:
            p = next(x for x in present if x["required"] == req)
            comparison_lines.append(f"✓ OFFER: {req} → CANDIDATE: {p['found_as']}")
        elif req in missing:
            comparison_lines.append(f"✗ OFFER: {req} → CANDIDATE: not found")

    total = len(requirements)
    fit_score = round(len(present) / max(total, 1) * 100)
    if fit_score >= 75:
        fit_label = "strong"
    elif fit_score >= 50:
        fit_label = "partial"
    else:
        fit_label = "weak"

    skills_matching_offer = _find_skills_matching_offer(
        skills, requirements, _build_job_query(titre, description, None),
        experiences=exp_list,
    )

    return {
        "requirements_checked": requirements,
        "present": present,
        "missing": missing,
        "comparison_lines": comparison_lines,
        "fit_score": fit_score,
        "fit_label": fit_label,
        "skills_matching_offer": skills_matching_offer,
    }


def _analyze_skill_gaps_semantic(
    skills: list[str],
    job_query: str,
    experiences: Optional[list[dict]] = None,
    latest_job: Optional[dict] = None,
    titre: Optional[str] = None,
    description: Optional[str] = None,
    threshold: float = GAP_MATCH_THRESHOLD,
) -> dict:
    if titre or description:
        return _build_offer_comparison(
            skills, experiences or [], titre, description, threshold
        )

    requirements = _extract_requirement_phrases(job_query)
    exp_list = experiences or []
    corpus = _build_evidence_corpus(skills, exp_list)

    if not requirements or not corpus:
        return {"requirements_checked": requirements, "present": [], "missing": []}

    embedder = _get_embedder()
    from sentence_transformers.util import cos_sim

    req_embs = embedder.encode(requirements, convert_to_tensor=True)
    corpus_embs = embedder.encode(corpus, convert_to_tensor=True)
    sim_matrix = cos_sim(req_embs, corpus_embs)

    present: list[dict] = []
    missing: list[str] = []

    for i, req in enumerate(requirements):
        sims = sim_matrix[i].tolist()
        best_idx = max(range(len(sims)), key=lambda j: sims[j])
        best_sim = sims[best_idx]
        evidence = corpus[best_idx][:80]

        if _accept_semantic_match(req, evidence, best_sim, "semantic"):
            present.append({
                "required": req,
                "found_as": corpus[best_idx][:80],
                "similarity": round(float(best_sim), 3),
            })
        elif _requirement_supported(req, corpus):
            support = next(item for item in corpus if _skills_match(req, item))
            present.append({
                "required": req,
                "found_as": support[:80],
                "similarity": 1.0,
            })
        else:
            missing.append(req)

    missing = _filter_spurious_gaps(missing, present, skills, exp_list, latest_job)
    missing = _clean_missing_gaps(missing)

    return {
        "requirements_checked": requirements,
        "present": present,
        "missing": missing,
    }



def _filter_spurious_gaps(
    missing: list[str],
    present: list[dict],
    skills: list[str],
    experiences: list[dict],
    latest_job: Optional[dict],
) -> list[str]:
    if not missing:
        return []

    present_reqs = {p["required"] for p in present}
    corpus = _build_evidence_corpus(skills, experiences)

    filtered: list[str] = []
    for req in missing:
        if req in present_reqs:
            continue
        if _looks_like_meta_label(req.strip()):
            continue
        if _requirement_supported(req, corpus):
            continue
        if not _is_plausible_requirement(req):
            continue
        if re.search(r"<[^>]+>", req):
            continue
        filtered.append(req)
    return filtered


def _dedupe_skills(skills: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for skill in skills:
        label = str(skill).strip()
        if not label:
            continue
        key = _normalize_skill_key(label)
        if key in seen:
            continue
        seen.add(key)
        result.append(label)
    return result


def _format_experience_text(exp: dict) -> str:
    role = str(exp.get("role") or "").strip()
    org = str(exp.get("entreprise") or exp.get("company") or "").strip()
    years = str(exp.get("years") or exp.get("dates") or "").strip()
    summary = str(exp.get("summary") or exp.get("description") or "").strip()
    head = " — ".join(p for p in [role, org, years] if p)
    if summary:
        return f"{head}. {summary}" if head else summary
    return head


def _build_chunks_from_extracted(experiences: list[dict], skills: list[str]) -> list[dict]:
    chunks: list[dict] = []
    for exp in experiences:
        text = _format_experience_text(exp)
        if len(text) >= 8:
            chunks.append({
                "text": text,
                "section": "experience",
                "weight": _SECTION_WEIGHTS["experience"],
            })
    for skill in skills:
        skill = str(skill).strip()
        if skill:
            chunks.append({
                "text": skill,
                "section": "skills",
                "weight": _SECTION_WEIGHTS["skills"],
            })
    return chunks


def _detect_language(skills: list[str], experiences: list[dict]) -> str:
    """
    Detects the CV language for internal processing purposes only.
    The summary output is ALWAYS in English regardless of this value.
    """
    parts = list(skills) + [_format_experience_text(e) for e in experiences]
    sample = " ".join(parts).lower()[:2000]
    if not sample.strip():
        return "fr"
    fr_markers = ["expérience", "compétences", "formation", "étudiant", "développement", "stagiaire"]
    en_markers = ["experience", "skills", "education", "student", "developer", "intern"]
    fr_score = sum(1 for m in fr_markers if m in sample)
    en_score = sum(1 for m in en_markers if m in sample)
    return "fr" if fr_score >= en_score else "en"


def _features_from_extracted(skills: list[str], experiences: list[dict]) -> dict:
    # cv_language kept for internal use; summary is always English
    cv_language = _detect_language(skills, experiences)
    latest_job = _select_latest_professional_job(experiences)

    latest_role_hint = None
    latest_job_role = None
    latest_job_company = None
    latest_job_dates = None
    if latest_job:
        latest_job_role = str(latest_job.get("role") or "").strip() or None
        latest_job_company = str(
            latest_job.get("entreprise") or latest_job.get("company") or ""
        ).strip() or None
        latest_job_dates = str(latest_job.get("years") or latest_job.get("dates") or "").strip() or None
        latest_role_hint = " | ".join(
            p for p in [latest_job_role, latest_job_company, latest_job_dates] if p
        ) or None

    return {
        "language": "en",           # Always English for output
        "cv_language": cv_language, # Original CV language (for internal use)
        "latest_role_hint": latest_role_hint,
        "latest_job_role": latest_job_role,
        "latest_job_company": latest_job_company,
        "latest_job_dates": latest_job_dates,
        "sentence1_hint": _build_sentence1_hint(latest_job),  # Always English
        "experience_count": len(experiences),
        "skills_detected": skills,
        "experiences": experiences,
    }


def _build_job_query(titre: Optional[str], description: Optional[str], type_contrat: Optional[str]) -> str:
    parts = []
    if titre:
        parts.append(f"Job title: {_strip_html(titre.strip())}")
    if type_contrat:
        parts.append(f"Contract: {type_contrat.strip()}")
    if description:
        parts.append(f"Requirements: {_strip_html(description.strip())[:1200]}")
    return " ".join(parts) if parts else "professional job requirements skills experience"


def _rank_chunks(chunks: list[dict], query: str, top_k: int = 6) -> list[dict]:
    if not chunks:
        return []

    embedder = _get_embedder()
    from sentence_transformers.util import cos_sim

    query_emb = embedder.encode(query, convert_to_tensor=True)
    texts = [c["text"] for c in chunks]
    chunk_embs = embedder.encode(texts, convert_to_tensor=True)
    sims = cos_sim(query_emb, chunk_embs)[0].tolist()

    ranked = []
    for chunk, sim in zip(chunks, sims):
        score = float(sim) * float(chunk.get("weight", 0.6))
        ranked.append({**chunk, "similarity": round(float(sim), 3), "rank_score": round(score, 3)})

    ranked.sort(key=lambda x: x["rank_score"], reverse=True)
    return ranked[:top_k]


def _match_skills_to_offer(
    skills: list[str],
    job_query: str,
    experiences: Optional[list[dict]] = None,
    top_n: int = 8,
) -> list[dict]:
    requirements = _extract_requirement_phrases(job_query)
    matched_names = _find_skills_matching_offer(
        skills, requirements, job_query, experiences=experiences, max_items=top_n
    )
    if not matched_names:
        return []
    return [{"skill": s, "similarity": 1.0} for s in matched_names]


def build_summary_context(
    skills: Optional[list[str]] = None,
    experiences: Optional[list[dict]] = None,
    titre_offre: Optional[str] = None,
    description: Optional[str] = None,
    type_contrat: Optional[str] = None,
    top_k: int = 6,
    gap_threshold: float = GAP_MATCH_THRESHOLD,
    cv_text: Optional[str] = None,
) -> dict:
    skill_list = _dedupe_skills([str(s).strip() for s in (skills or []) if str(s).strip()])
    exp_list = [e for e in (experiences or []) if isinstance(e, dict)]

    chunks = _build_chunks_from_extracted(exp_list, skill_list)
    features = _features_from_extracted(skill_list, exp_list)

    has_offer = bool(
        (titre_offre and titre_offre.strip())
        or (description and description.strip())
    )

    skill_gaps: dict = {"requirements_checked": [], "present": [], "missing": []}

    if has_offer:
        job_query = _build_job_query(titre_offre, description, type_contrat)
        top_chunks = _rank_chunks(chunks, job_query, top_k=top_k)
        matched_skills = _match_skills_to_offer(skill_list, job_query, experiences=exp_list)
        skill_gaps = _analyze_skill_gaps_semantic(
            skill_list,
            job_query,
            experiences=exp_list,
            latest_job=_select_latest_professional_job(exp_list),
            titre=titre_offre,
            description=description,
            threshold=gap_threshold,
        )
        if "skills_matching_offer" not in skill_gaps:
            reqs = skill_gaps.get("requirements_checked") or _extract_offer_requirements(
                titre_offre, description
            )
            skill_gaps["skills_matching_offer"] = _find_skills_matching_offer(
                skill_list, reqs, job_query, experiences=exp_list
            )
        avg_sim = round(
            sum(c["similarity"] for c in top_chunks) / max(len(top_chunks), 1),
            3,
        )
    else:
        job_query = "professional profile experience skills achievements"
        top_chunks = _rank_chunks(chunks, job_query, top_k=top_k)
        matched_skills = []
        avg_sim = round(
            sum(c["similarity"] for c in top_chunks) / max(len(top_chunks), 1),
            3,
        )

    return {
        "features": features,
        "job_query": job_query,
        "top_chunks": top_chunks,
        "matched_skills": matched_skills,
        "skill_gaps": skill_gaps,
        "semantic_match_score": avg_sim,
        "has_offer": has_offer,
        "offer_title": _strip_html((titre_offre or "").strip()) or None,
    }


def compose_summary(ctx: dict) -> str:
    """
    Deterministic fallback — used if the LLM fails.
    Always produces an English narrative summary.
    Performs direct skill-vs-requirement comparison for accurate gaps.
    """
    f = ctx["features"]
    gaps = ctx.get("skill_gaps") or {}
    has_offer = ctx.get("has_offer", False)

    candidate_skills = [s.lower() for s in (f.get("skills_detected") or [])]
    matched = gaps.get("skills_matching_offer") or []
    fit_score = gaps.get("fit_score", 0)
    fit_label = gaps.get("fit_label", "unknown")
    offer_title = ctx.get("offer_title") or "this role"

    # --- Sentence 1: matched skills ---
    parts: list[str] = []
    if matched:
        parts.append(
            "The candidate's strongest relevant skills for this role include "
            + ", ".join(matched[:6]) + "."
        )
    else:
        parts.append(
            "The candidate does not appear to have directly matching skills for this role."
        )

    # --- Sentence 2: gaps (use cosine missing + any requirements not in skills) ---
    cosine_missing = (gaps.get("missing") or [])[:4]
    if cosine_missing:
        parts.append(
            "However, key missing skills that limit their fit include "
            + ", ".join(cosine_missing) + "."
        )

    # --- Sentence 3: recommendation ---
    fit_word = {"strong": "strong", "partial": "partial", "weak": "weak"}.get(fit_label, "limited")
    rec = {
        "strong": "advancing",
        "partial": "considering with caution",
        "weak": "rejecting",
    }.get(fit_label, "evaluating")
    parts.append(
        f"Based on a {fit_word} overall fit ({fit_score}% of requirements covered) "
        f"for the role «{offer_title}», I recommend {rec} this candidate."
    )

    return " ".join(parts)


def format_context_for_prompt(ctx: dict, compact: bool = False) -> str:
    """Formats context for the LLM prompt. Always in English."""
    f = ctx["features"]
    all_confirmed_skills = ", ".join(f.get("skills_detected") or []) or "none"
    max_exp_chars = 120 if compact else 500

    lines = [
        "--- CANDIDATE DATA (pre-extracted, do not re-parse CV) ---",
        f"CV Language (detected): {f.get('cv_language', 'unknown')} | Summary output: ALWAYS English",
    ]
    if not compact:
        lines.extend([
            f"Experience count: {f.get('experience_count', 0)}",
            f"Semantic match score: {ctx.get('semantic_match_score', 0)}",
            "",
        ])
    else:
        lines.append("")

    if ctx.get("has_offer"):
        gaps = ctx.get("skill_gaps") or {}
        fit = gaps.get("fit_score", 0)
        label = gaps.get("fit_label", "unknown")
        lines.extend([
            "",
            "--- COMPUTED FIT SCORE (DO NOT RECALCULATE — USE VERBATIM) ---",
            f"Offer: {ctx.get('offer_title') or 'not specified'}",
            f"Fit score: {fit}%",
            f"Fit label: {label}",
            f"Use exactly '{fit}%' and '{label}' in your summary. Never invent a different number.",
            "",
        ])

    lines.extend([
        "--- LAST PROFESSIONAL JOB (MANDATORY for opening sentence) ---",
        f"Role: {f.get('latest_job_role') or 'not available'}",
        f"Company: {f.get('latest_job_company') or 'not available'}",
        f"Dates: {f.get('latest_job_dates') or 'not available'}",
        f"Opening sentence template (copy verbatim): {f.get('sentence1_hint') or 'not available'}",
    ])

    gaps = ctx.get("skill_gaps") or {}
    skills_for_sentence2 = gaps.get("skills_matching_offer") or []

    lines.extend(["", "--- SKILLS MATCHING OFFER (Sentence 1 — cite ONLY these, literally) ---"])
    if skills_for_sentence2:
        lines.append(", ".join(skills_for_sentence2[:6]))
        lines.append(
            "Do NOT mention any tool or technology unless it appears in this list "
            "or literally in EXTRACTED EXPERIENCES below."
        )
    else:
        lines.append("NONE — the candidate has no directly matching extracted skills for this offer.")
        lines.append(
            "Sentence 1 must state limited direct skill match and describe their actual background "
            "from EXTRACTED EXPERIENCES only. Do NOT invent tools or technologies."
        )
    lines.append("")

    lines.extend([
        "--- EXTRACTED EXPERIENCES ---",
    ])
    exp_list = f.get("experiences") or []
    if exp_list:
        sorted_exps = sorted(
            exp_list,
            key=lambda e: _parse_years_sort_key(str(e.get("years") or e.get("dates") or "")),
            reverse=True,
        )
        for i, exp in enumerate(sorted_exps, 1):
            tag = " [project]" if _is_personal_project(exp) else " [professional]"
            exp_text = _format_experience_text(exp)
            if compact and len(exp_text) > max_exp_chars:
                exp_text = exp_text[:max_exp_chars].rstrip() + "…"
            lines.append(f"{i}.{tag} {exp_text}")
    else:
        lines.append("none")

    if gaps.get("comparison_lines"):
        fit = gaps.get("fit_score", 0)
        label = gaps.get("fit_label", "unknown")
        lines.extend([
            "",
            f"--- OFFER vs CANDIDATE MATRIX (fit={fit}% — {label}) ---",
            "PRIMARY source for strengths and gaps. Each ✓ = strength. Each ✗ = confirmed gap.",
        ])
        for cl in gaps["comparison_lines"]:
            lines.append(cl)

        lines.extend(["", "Confirmed MISSING (only these gaps are valid):"])
        if gaps.get("missing"):
            for m in gaps["missing"]:
                lines.append(f"  ✗ {m}")
        else:
            lines.append("  NONE — skip Sentence 2 entirely; do not invent any gap.")
        lines.append(
            "Technologies mentioned in EXTRACTED EXPERIENCES count as present — never report them as missing."
        )

    return "\n".join(lines)