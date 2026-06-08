"""Structure and normalize fields produced by the RoBERTa NER CV extractor."""

from __future__ import annotations

import re
import json
from typing import Callable, Optional

from cv_ner_extractor import extract_raw, format_entities_for_prompt

CV_EXCERPT_CHARS = 6000
EXPERIENCE_EXCERPT_CHARS = 12000

_GENERIC_PROJECT_ROLES = frozenset({
    "développeur", "developpeur", "developer", "développeuse", "developpeuse",
    "ingénieur", "ingenieur", "engineer", "projet", "projet personnel",
    "projets personnels", "personal project", "projects", "project",
    "étudiant", "etudiant", "student",
})

_INVALID_ROLE_TOKENS = frozenset({
    "fine", "gpt", "gpt-2", "gpt2", "bert", "sentence", "tuning", "agent",
    "news", "lexi", "cerebri", "ia", "ml", "nlp", "api", "web", "app",
    "de", "et", "le", "la", "un", "une", "des", "du", "pour", "avec",
    "projet", "project", "stage", "intern", "solution", "système", "systeme",
})

_PLACEHOLDER_VALUES = frozenset({
    "non spécifié", "non specifie", "non spécifie", "non precise",
    "n/a", "na", "none", "unknown", "inconnu", "—", "-", "null",
})

_CERT_LIKE_COMPANIES = (
    "nvidia", "aws", "amazon web services", "google cloud", "microsoft",
    "coursera", "udemy", "linkedin learning", "datacamp", "simplilearn",
    "oracle university", "ibm", "meta", "facebook", "comptia", "cisco",
    "openclassrooms", "edx", "deeplearning.ai",
)


def _cv_excerpt(text: str) -> str:
    return (text or "").strip()[:CV_EXCERPT_CHARS]


def _run_structuring_prompt(
    prompt: str,
    infer_json: Callable,
    parse_json: Callable,
    model: str,
    max_tokens: int,
    seed: Optional[int] = None,
    temperature: float = 0.0,
) -> dict:
    def _infer(p: str, max_tokens: int, model: str) -> str:
        return infer_json(
            p, max_tokens=max_tokens, model=model, seed=seed, temperature=temperature
        )

    raw = _infer(prompt, max_tokens, model)
    return parse_json(raw)


def _stable_sort_skills(skills: list[str]) -> list[str]:
    return sorted(
        skills,
        key=lambda s: (re.sub(r"[-_\s]", "", s.lower()), s.lower()),
    )


def _is_missing_value(value: str) -> bool:
    v = (value or "").strip().lower()
    return not v or v in _PLACEHOLDER_VALUES


def _clean_field(value: str) -> str:
    v = (value or "").strip()
    return "" if _is_missing_value(v) else v


def _default_non_specifie(value: str) -> str:
    return _clean_field(value) or "Non spécifié"


def _is_valid_project_name(name: str) -> bool:
    n = (name or "").strip()
    if len(n) < 5:
        return False
    if n.lower() in _INVALID_ROLE_TOKENS:
        return False
    if re.match(r"^[A-Z][a-z0-9]+([A-Z][a-zA-Z0-9]+)+$", n):
        return True
    return False


def _is_valid_experience_entry(exp: dict) -> bool:
    role = (exp.get("role") or "").strip()
    if not role:
        return False
    low = role.lower()
    if low in _INVALID_ROLE_TOKENS or low in _GENERIC_PROJECT_ROLES:
        return False
    if "stagiaire" in low or "intern" in low or "stage" in low:
        return True
    company = _clean_field(str(exp.get("entreprise", "")))
    if company:
        return len(role) >= 3
    if _is_valid_project_name(role):
        return True
    summary = (exp.get("summary") or "").strip()
    return len(summary) >= 50 and len(role) >= 6


def _split_merged_projects(entry: dict) -> list[dict]:
    summary = (entry.get("summary") or "").strip()
    role = (entry.get("role") or "").strip()
    if role.lower() not in _GENERIC_PROJECT_ROLES or not summary:
        return [entry]

    entreprise = _default_non_specifie(str(entry.get("entreprise", "")))
    years = _default_non_specifie(str(entry.get("years", "")))

    starters = list(
        re.finditer(r"(?<![\w-])([A-ZÀ-ÖØ-Þ][\w\d]{2,})\s*[-–—]\s*", summary)
    )
    segments: list[dict] = []
    for i, m in enumerate(starters):
        name = m.group(1).strip()
        if not _is_valid_project_name(name):
            continue
        desc_start = m.end()
        desc_end = starters[i + 1].start() if i + 1 < len(starters) else len(summary)
        desc = summary[desc_start:desc_end].strip().strip(",").strip()
        segments.append({
            "role": name,
            "entreprise": entreprise,
            "years": years,
            "summary": desc,
        })

    return segments if len(segments) >= 2 else [entry]


def _normalize_experience_entry(exp: dict) -> dict | None:
    role = str(exp.get("role", "")).strip()
    if not role:
        return None
    return {
        "role": role,
        "entreprise": _default_non_specifie(str(exp.get("entreprise", ""))),
        "years": _default_non_specifie(str(exp.get("years", ""))),
        "summary": str(exp.get("summary", "")).strip(),
    }


def _expand_experiences(entries: list[dict]) -> list[dict]:
    expanded: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for raw in entries:
        if not isinstance(raw, dict):
            continue
        base = _normalize_experience_entry(raw)
        if not base or _is_cert_like_false_job(base):
            continue

        for piece in _split_merged_projects(base):
            norm = _normalize_experience_entry(piece)
            if not norm or _is_cert_like_false_job(norm) or not _is_valid_experience_entry(norm):
                continue
            key = (norm["role"].lower(), (norm["summary"] or "")[:80].lower())
            if key in seen:
                continue
            seen.add(key)
            expanded.append(norm)

    return expanded


def _is_cert_like_false_job(exp: dict) -> bool:
    role = (exp.get("role") or "").lower()
    company = (exp.get("entreprise") or "").lower()
    summary = (exp.get("summary") or "").strip()
    years = (exp.get("years") or "").strip()

    if summary:
        return False
    if not _is_missing_value(years) and years.lower() != "non spécifié":
        return False
    if any(tok in company for tok in _CERT_LIKE_COMPANIES):
        return True
    if "nvidia" in company and "stagiaire" not in role and "intern" not in role and "stage" not in role:
        return True
    return False


_SKILL_HEADERS = (
    r"(?i)\b(?:"
    r"COMPÉTENCES|COMPETENCES|SKILLS|TECHNICAL\s+SKILLS|"
    r"TECHNICAL\s+COMPETENCIES|CORE\s+COMPETENCIES|KEY\s+SKILLS|"
    r"OUTILS|TOOLS|TECHNOLOGIES|TECH\s+STACK|STACK"
    r")\b"
)

_SECTION_END = (
    r"(?i)\b(?:"
    r"EXPÉRIENCE|EXPERIENCES?|EXPERIENCE|WORK\s+EXPERIENCE|PROFESSIONAL\s+EXPERIENCE|"
    r"PROJETS?|PROJECTS?|"
    r"LANGUES|LANGUAGES|"
    r"CERTIFICATIONS?|CERTIFICATS?|CERTIFICATES?|"
    r"EDUCATION|ÉDUCATION|FORMATION|ÉTUDES|"
    r"INTERESTS?|REFERENCES?|PUBLICATIONS?"
    r")\b"
)

_GENERIC_SKILL_HEADERS = re.compile(
    r"^(compétences|competences|skills|technologies|tools|technical\s+skills?)\s*:?\s*$",
    re.IGNORECASE,
)

_MAX_SKILL_WORDS = 5
_MAX_SKILL_CHARS = 50
_MAX_SKILL_SECTION_CHARS = 1200

_MONTH_OR_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")

_SKILL_LIST_SPLIT = re.compile(
    r"[,;|/]|(?:\s+•\s+)|(?:\s+and\s+)|(?:\s+et\s+)|(?:\s*&\s*)",
    re.IGNORECASE,
)


def _truncate_at_section_end(text: str, fallback_max: int = 800) -> str:
    if not text:
        return ""
    end = re.search(_SECTION_END, text)
    if end:
        return text[: end.start()].strip()
    return text[:fallback_max].strip()


def _is_plausible_skill_label(label: str) -> bool:
    """Keep short tool/tech labels; drop sentences, jobs, certs, locations."""
    text = re.sub(r"\s+", " ", (label or "").strip().strip("•·-*–—|,;:"))
    if not text or len(text) < 2:
        return False
    if len(text) > _MAX_SKILL_CHARS:
        return False
    if "\n" in text or "\r" in text:
        return False
    if "(" in text or ")" in text:
        return False
    if text.count(":") >= 1:
        return False
    if text.count(".") > 1:
        return False
    if text.count(",") > 1 or text.count(";") > 1:
        return False
    if _MONTH_OR_YEAR.search(text):
        return False
    if re.search(r"\b\d{4}\b", text):
        return False
    words = text.split()
    if len(words) > _MAX_SKILL_WORDS:
        return False
    if any(len(w) > 22 for w in words):
        return False
    if len(words) >= 3 and len(text) > 30:
        return False
    if re.fullmatch(r"\d+[dD]", text):
        return False
    if len(text) <= 2 and not re.search(r"[A-Za-z]{2}", text):
        return False
    return True


def _filter_skill_labels(skills: list[str]) -> list[str]:
    return _dedupe_skill_labels([s for s in skills if _is_plausible_skill_label(s)])


def _section_block_looks_structured(block: str) -> bool:
    """Reject flat CV blobs mistaken for a skills section."""
    if not block or len(block) > _MAX_SKILL_SECTION_CHARS:
        return False
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines or len(lines) > 20:
        return False
    avg_len = sum(len(ln) for ln in lines) / len(lines)
    if avg_len > 100:
        return False
    long_lines = sum(1 for ln in lines if len(ln) > 120)
    return long_lines <= 1


def _extract_skills_section_block(text: str, max_chars: int = _MAX_SKILL_SECTION_CHARS) -> str:
    if not text:
        return ""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    block_lines: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if not in_section:
            header_match = re.search(_SKILL_HEADERS, stripped)
            if header_match:
                in_section = True
                remainder = stripped[header_match.end():].strip()
                if remainder:
                    end_in_line = re.search(_SECTION_END, remainder)
                    chunk = remainder[: end_in_line.start()].strip() if end_in_line else _truncate_at_section_end(remainder)
                    if chunk:
                        block_lines.append(chunk)
                    if end_in_line:
                        break
            continue
        if stripped and re.search(_SECTION_END, stripped):
            break
        if stripped:
            if len(stripped) > 120:
                block_lines.append(_truncate_at_section_end(stripped))
            else:
                block_lines.append(stripped)
    if block_lines:
        return "\n".join(block_lines)[:max_chars]
    flat = re.sub(r"\s+", " ", text).strip()
    m = re.search(_SKILL_HEADERS, flat)
    if not m:
        return ""
    rest = flat[m.end():]
    return _truncate_at_section_end(rest, fallback_max=max_chars)[:max_chars]


def _split_skill_candidates(raw: str) -> list[str]:
    """Split a skills block into labels — no fixed tech vocabulary."""
    if not raw:
        return []
    items: list[str] = []
    seen: set[str] = set()

    def add(label: str) -> None:
        label = re.sub(r"\s+", " ", (label or "").strip().strip("•·-*–—|,;:"))
        if not _is_plausible_skill_label(label):
            return
        if _GENERIC_SKILL_HEADERS.match(label):
            return
        if re.match(r"^(email|phone|tel|linkedin|github|address|www\.|http)", label, re.I):
            return
        key = label.lower()
        if key in seen:
            return
        seen.add(key)
        items.append(label)

    def add_parts(chunk: str) -> None:
        parts = _SKILL_LIST_SPLIT.split(chunk)
        if len(parts) > 1:
            for part in parts:
                add(part)
        else:
            add(chunk)

    for line in raw.split("\n"):
        line = re.sub(r"^[\u2022\ufffd\u2023\*\-–]\s*", "", line.strip())
        if not line or not _is_plausible_skill_label(line) and ":" not in line and len(line.split()) > _MAX_SKILL_WORDS:
            continue
        if ":" in line:
            value_segments = line.split(":")[1:]
            for seg in value_segments:
                add_parts(seg)
            continue
        add_parts(line)

    return items


def _extract_skills_from_sections(cv_text: str) -> list[str]:
    block = _extract_skills_section_block(cv_text)
    if not block or not _section_block_looks_structured(block):
        return []
    return _split_skill_candidates(block)


def _ner_skill_labels(ner_payload: dict) -> list[str]:
    by_label = ner_payload.get("by_label") or {}
    labels: list[str] = []
    seen: set[str] = set()
    for ent in by_label.get("SKILL", []):
        text = str(ent.get("text", "")).strip()
        if not _is_plausible_skill_label(text):
            continue
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            labels.append(text)
    return labels


def _skill_appears_in_cv(skill: str, cv_text: str) -> bool:
    if not skill or not cv_text:
        return False
    sl = skill.strip().lower()
    if len(sl) < 2:
        return False
    cv = cv_text.lower()
    if sl in cv:
        return True
    compact_skill = re.sub(r"[\s_\-./]", "", sl)
    compact_cv = re.sub(r"[\s_\-./]", "", cv)
    return len(compact_skill) >= 2 and compact_skill in compact_cv


def _dedupe_skill_labels(skills: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for skill in skills:
        label = str(skill).strip()
        if not label:
            continue
        key = re.sub(r"[-_\s]", "", label.lower())
        if key in seen:
            continue
        seen.add(key)
        result.append(label)
    return result


def _merge_skill_sources(
    llm_skills: list[str],
    ner_skills: list[str],
    section_skills: list[str],
    cv_text: str,
) -> list[str]:
    """LLM output first; add only short NER/section labels the LLM missed."""
    merged: list[str] = []
    seen: set[str] = set()

    def add(skill: str) -> None:
        label = str(skill).strip()
        if not _is_plausible_skill_label(label):
            return
        key = re.sub(r"[-_\s]", "", label.lower())
        if key in seen:
            return
        seen.add(key)
        merged.append(label)

    for skill in llm_skills:
        add(skill)

    llm_keys = set(seen)
    for skill in ner_skills + section_skills:
        if not _is_plausible_skill_label(skill) or not _skill_appears_in_cv(skill, cv_text):
            continue
        key = re.sub(r"[-_\s]", "", skill.strip().lower())
        if key in llm_keys:
            continue
        add(skill)
    return merged


def refine_skills(
    cv_text: str,
    infer_json: Callable,
    parse_json: Callable,
    model: str,
    ner_payload: Optional[dict] = None,
    seed: Optional[int] = None,
) -> list[str]:
    payload = ner_payload or extract_raw(cv_text)
    cv = (cv_text or "").strip()
    entities_json = format_entities_for_prompt(payload["by_label"])
    ner_skills = _ner_skill_labels(payload)
    section_skills = _extract_skills_from_sections(cv)
    hint_skills = _filter_skill_labels(ner_skills + section_skills)

    prompt = f"""You are a CV data cleaner. A RoBERTa NER model extracted entities from this CV.
The NER output may contain errors, duplicates, merged text, cities, or full sentences mislabeled as skills.

NER entities by label:
{entities_json}

Candidate skills detected in the dedicated skills section or as SKILL entities (verify, split, normalize):
{json.dumps(hint_skills, ensure_ascii=False) if hint_skills else "[]"}

CV text (source of truth):
{_cv_excerpt(cv)}

Task: produce a clean list of technical skills, tools, frameworks, libraries, databases, and methods.

Rules:
- Primary source: the COMPÉTENCES / SKILLS section and explicit technology names in projects
- Each item = ONE short label (1-4 words max): "Python", "Docker", "Machine Learning", "REST API"
- Split merged strings ("Python Docker" → two skills; "TypeScript Machine Learning" → two skills)
- EXCLUDE completely:
  * job titles, role names, company names, school names, cities, countries
  * certification titles and training course names (Udemy, NVIDIA courses, etc.)
  * spoken languages and proficiency levels (Français, Anglais, Arabe, etc.)
  * dates, durations, narrative sentences, bullet descriptions from experience blocks
  * section headers and category labels (e.g. "Développement Logiciel", "Base de données")
- Do not invent skills absent from the CV
- Typical output: 15-40 skills for a standard CV, not hundreds

Respond ONLY with valid JSON:
{{"skills": ["skill1", "skill2"]}}"""

    result = _run_structuring_prompt(
        prompt, infer_json, parse_json, model, max_tokens=900, seed=seed, temperature=0.0
    )
    llm_skills = result.get("skills") or []
    llm_clean = _filter_skill_labels([str(s).strip() for s in llm_skills if isinstance(s, str)])
    merged = _merge_skill_sources(llm_clean, ner_skills, section_skills, cv)
    return _stable_sort_skills(merged)


def refine_experiences(
    cv_text: str,
    infer_json: Callable,
    parse_json: Callable,
    model: str,
    ner_payload: Optional[dict] = None,
) -> list[dict]:
    payload = ner_payload or extract_raw(cv_text)
    entities_json = format_entities_for_prompt(payload["by_label"])
    cert_hints = format_entities_for_prompt(
        {k: v for k, v in payload.get("by_label", {}).items() if k in ("CERTIFICATION", "DEGREE")}
    )

    prompt = f"""You are a CV data cleaner. A RoBERTa NER model extracted entities from this CV.
Labels: JOB_TITLE, COMPANY, DATE, EXPERIENCE_DESC.

NER entities by label:
{entities_json}

CERTIFICATION / DEGREE hints (must NOT be listed as work experience):
{cert_hints or "(none)"}

CV text (source of truth):
{(cv_text or "").strip()[:EXPERIENCE_EXCERPT_CHARS]}

Task: produce ALL work experience entries: jobs, internships (stage), AND every personal/academic project listed in the CV.

Rules:
- Jobs/internships: group JOB_TITLE + COMPANY + DATE + EXPERIENCE_DESC; role = job title (e.g. "Stagiaire Data Scientist")
- Personal projects: ONE separate JSON entry per project — never merge several projects into one entry
- Personal project role = exact project name from the CV (e.g. "NovaMedica", "NewsBot", "LexiAI", "CerebriAI") — minimum 5 characters, CamelCase brand style; NEVER a single word like "GPT", "BERT", "Fine", "Sentence", "Développeur"
- For personal projects without employer or dates: entreprise = "Non spécifié" AND years = "Non spécifié" (use this exact label only for missing company/dates)
- Never split one project description into multiple entries; technology words inside a description are NOT project names
- years = dates as written in the CV for jobs/internships, or "Non spécifié" for projects without dates
- entreprise = company from the CV for jobs/internships, or "Non spécifié" for personal projects
- summary = description of that single project/job only (from the CV); "" if none — never invent text
- Include EVERY project mentioned in a Projects / Projets / Portfolio section
- Do NOT list certifications or vendor courses (NVIDIA, AWS, Coursera, etc.) as employment
- Do not invent entries absent from the CV

Respond ONLY with valid JSON:
{{
  "experiences": [
    {{"role": "...", "entreprise": "...", "years": "...", "summary": "..."}}
  ]
}}"""

    result = _run_structuring_prompt(prompt, infer_json, parse_json, model, max_tokens=2500)
    experiences = result.get("experiences") or []
    if not isinstance(experiences, list):
        return []
    return _expand_experiences(experiences)


def refine_certifications(
    cv_text: str,
    infer_json: Callable,
    parse_json: Callable,
    model: str,
    ner_payload: Optional[dict] = None,
) -> list[dict]:
    payload = ner_payload or extract_raw(cv_text)
    entities_json = format_entities_for_prompt(payload["by_label"])

    prompt = f"""You are a CV data cleaner. A RoBERTa NER model extracted entities from this CV.
Labels: CERTIFICATION, DEGREE, INSTITUTION, DATE.

NER entities by label:
{entities_json}

CV text (source of truth):
{_cv_excerpt(cv_text)}

Task: produce certifications and diplomas as separate clean entries.

Rules:
- One entry per certification or diploma — never merge multiple items into one
- nom = exact title as in CV (short, not a paragraph)
- organisme = issuing school/organization or null
- annee = year or range as written, or null
- type = "certification" for professional/online certs, "diploma" for degrees (bachelor, master, baccalauréat, cycle ingénieur, etc.)
- Split wrongly merged NER spans (e.g. baccalauréat + skills list + certifications in one blob → separate entries)
- Exclude skills, languages, and work experience from this list
- Do not invent entries absent from the CV

Respond ONLY with valid JSON:
{{
  "certifications": [
    {{"nom": "...", "organisme": null, "annee": null, "type": "certification|diploma"}}
  ]
}}"""

    result = _run_structuring_prompt(prompt, infer_json, parse_json, model, max_tokens=1800)
    certifications = result.get("certifications") or []
    normalized = []
    for cert in certifications:
        if not isinstance(cert, dict) or not cert.get("nom"):
            continue
        nom = str(cert.get("nom", "")).strip()
        if len(nom) < 3 or len(nom) > 200:
            continue
        org = cert.get("organisme")
        normalized.append({
            "nom":       nom,
            "organisme": str(org).strip() if org else None,
            "annee":     str(cert["annee"]).strip() if cert.get("annee") else None,
            "type":      str(cert.get("type") or "certification").strip(),
        })
    return normalized


def refine_companies(
    cv_text: str,
    infer_json: Callable,
    parse_json: Callable,
    model: str,
    ner_payload: Optional[dict] = None,
) -> list[dict]:
    payload = ner_payload or extract_raw(cv_text)
    entities_json = format_entities_for_prompt(payload["by_label"])

    prompt = f"""You are a CV data cleaner. A RoBERTa NER model extracted COMPANY entities.

NER entities:
{entities_json}

CV text:
{_cv_excerpt(cv_text)}

Task: list companies mentioned in work/internship context only.

Rules:
- One entry per distinct company
- Only include what is explicitly in the CV
- Fields not mentioned = null

Respond ONLY with valid JSON:
{{
  "companies": [
    {{"nom": "...", "secteur": null, "ville": null, "site_web": null, "email": null, "telephone": null}}
  ]
}}"""

    result = _run_structuring_prompt(prompt, infer_json, parse_json, model, max_tokens=600)
    companies = result.get("companies") or []
    if not isinstance(companies, list):
        return []
    return companies
