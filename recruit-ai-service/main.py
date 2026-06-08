from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from groq import Groq
import re
import json
import os
import time
import logging
from dotenv import load_dotenv
import hashlib
import statistics

import httpx
from groq import Groq, APITimeoutError

from match_scoring import compute_match_score, rank_candidates_for_offer
from cv_ner_extractor import extract_raw
from cv_ner_refiner import (
    refine_skills,
    refine_experiences,
    refine_certifications,
    refine_companies,
)
from fraud_predictor import predict_candidate as predict_fraud
from cv_file_extractor import extract_cv_text_from_file_bytes
from preprocess_cv_text import preprocess_cv_text
from summary_pipeline import (
    build_summary_context,
    format_context_for_prompt,
    compose_summary,
    _dedupe_skills,
    _build_sentence1_hint,
    _select_latest_professional_job,
    _parse_years_sort_key,
    _strip_html,
)

load_dotenv()
logger = logging.getLogger("recruit-ai")

def stable_seed(text: str) -> int:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % (2**31 - 1)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY manquante dans .env")

client = Groq(
    api_key=GROQ_API_KEY,
    timeout=httpx.Timeout(120.0, connect=60.0),
)
MODEL_LARGE = "llama-3.3-70b-versatile"
MODEL_FAST  = "llama-3.1-8b-instant"
MODEL_SUMMARY = MODEL_FAST

_RETRYABLE = (
    APITimeoutError,
    httpx.TimeoutException,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
)

app = FastAPI(title="RecruitSaaS AI Service", version="5.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic ───────────────────────────────────────────────────────────────────
class CvRequest(BaseModel):
    texteExtrait: str

class CvFileExtractResponse(BaseModel):
    texteExtrait: str
    usedOcr: bool = False
    ocrPages: List[int] = []
    pageCount: int = 0
    warnings: List[str] = []

class EvalContextRequest(BaseModel):
    texteExtrait: str
    titreOffre:  Optional[str] = None
    description: Optional[str] = None
    typeContrat: Optional[str] = None
    skills:      Optional[List[str]] = None
    experiences: Optional[List[dict]] = None
    summaryLanguage: Optional[str] = "en"   # kept for API compat, output is always English
    candidatureId: Optional[str] = None
    offreId: Optional[str] = None

EvalRequest = EvalContextRequest
CvContextRequest = CvRequest


@app.post("/ai/extract-cv-text", response_model=CvFileExtractResponse)
async def extract_cv_text(
    file: UploadFile = File(...),
    ocrPdfIfNeeded: bool = True,
    forcePdfOcr: bool = False,
    lang: str = "fra+eng",
):
    """
    Extract raw CV text from an uploaded file.

    - PDF: PyMuPDF text extraction + OCR fallback on scanned pages.
    - Image: Tesseract OCR after preprocessing (deskew/denoise/CLAHE/Otsu/upscale).
    """
    filename = file.filename or "cv"
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")

    try:
        out = extract_cv_text_from_file_bytes(
            data,
            filename,
            ocr_pdf_if_needed=ocrPdfIfNeeded,
            force_pdf_ocr=forcePdfOcr,
            lang=lang,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"extract-cv-text failed: {exc}")

    if not out.text or len(out.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="CV text too short (possibly scanned/unreadable).")

    return CvFileExtractResponse(
        texteExtrait=out.text,
        usedOcr=out.used_ocr,
        ocrPages=out.ocr_pages,
        pageCount=out.page_count,
        warnings=out.warnings,
    )

class InterviewQuestionsRequest(BaseModel):
    titreOffre:       str
    descriptionOffre: Optional[str] = None
    cvResume:         Optional[str] = None
    competences:      Optional[List[str]] = None
    nombreQuestions:  Optional[int] = 8

class EvaluateAnswerRequest(BaseModel):
    question:      str
    reponse:       str
    titreOffre:    Optional[str] = None
    indexQuestion: Optional[int] = 0

class FraudMetricsRequest(BaseModel):
    tab_changes: int = 0
    window_blurs: int = 0
    no_face_count: int = 0
    multi_face_count: int = 0
    face_absence_ratio: float = 0.0
    gaze_away_count: int = 0
    gaze_away_ratio: float = 0.0
    gaze_down_count: int = 0
    gaze_down_ratio: float = 0.0
    gaze_horizontal_count: int = 0
    gaze_horizontal_ratio: float = 0.0
    phone_likely_count: int = 0
    face_partial_count: int = 0
    face_checks: int = 0
    phone_detected: int = 0
    book_detected: int = 0
    laptop_detected: int = 0
    extra_person: int = 0
    suspicious_obj_count: int = 0
    answer_delay: float = 1.5
    answer_speed: float = 2.0
    frontend_fraud_score: float = 0.05

class GenerateReportRequest(BaseModel):
    titreOffre:   str
    nomCandidat:  str
    questions:    List[dict]
    dureeMinutes: Optional[int] = 30
    fraudMetrics: Optional[FraudMetricsRequest] = None
    verificationFacialeOk: Optional[bool] = None

class GenerateQuizRequest(BaseModel):
    titreOffre:    str
    description:   Optional[str] = None
    num_questions: int = 10


class RankCandidatesRequest(BaseModel):
    titreOffre: str
    description: Optional[str] = None
    typeContrat: Optional[str] = None
    offreId: Optional[str] = None
    candidates: List[dict] = []
    topK: Optional[int] = None

# ── Text cleaner ───────────────────────────────────────────────────────────────
def clean_cv_text(text: str) -> str:
    text = re.sub(r'([a-zàâäéèêëîïôùûüç])([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r' {2,}', ' ', text)
    sections = ['Profil', 'Compétences', 'Competences', 'Expérience professionnelle',
                'Expérience', 'Experience', 'Projets', 'Projects',
                'Formation', 'Education', 'Certifications', 'Langues', 'Skills', 'Summary']
    for s in sections:
        text = text.replace(s, f'\n{s}')
    return text.strip()

# ── Core helpers ───────────────────────────────────────────────────────────────
def _is_retryable_groq_error(exc: Exception) -> bool:
    if isinstance(exc, _RETRYABLE):
        return True
    err = str(exc).lower()
    return any(k in err for k in (
        "rate", "429", "timeout", "timed out", "overloaded", "503", "502", "connect",
    ))


def call_groq(
    prompt: str,
    max_tokens: int = 600,
    model: str = None,
    system: Optional[str] = None,
    seed: Optional[int] = None,
    temperature: float = 0.3,
) -> str:
    m = model or MODEL_LARGE
    system_content = system or (
        "You are a precise assistant. "
        "You ALWAYS respond with valid JSON only — no markdown, no explanation, no extra text."
    )
    use_seed = seed
    last_err: Exception | None = None
    max_attempts = 5

    for attempt in range(max_attempts):
        kwargs = dict(
            model=m,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user",   "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if use_seed is not None:
            kwargs["seed"] = use_seed
        try:
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            if not content or not str(content).strip():
                raise ValueError("Groq returned empty content")
            return str(content).strip()
        except Exception as e:
            last_err = e
            err = str(e).lower()
            logger.warning("Groq attempt %s/%s failed (%s): %s", attempt + 1, max_attempts, m, e)
            if use_seed is not None and "seed" in err:
                use_seed = None
                continue
            if attempt < max_attempts - 1 and _is_retryable_groq_error(e):
                time.sleep(min(3 * (2 ** attempt), 30))
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("Groq call failed")

def parse_json(text: str) -> dict:
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if not match:
        summary_match = re.search(r'"summary"\s*:\s*"(.+)"\s*\}', clean, re.DOTALL)
        if summary_match:
            return {"summary": summary_match.group(1).replace('\\"', '"')}
        raise ValueError(f"No JSON found in: {text[:200]}")
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        summary_match = re.search(r'"summary"\s*:\s*"(.+)"\s*\}', clean, re.DOTALL)
        if summary_match:
            return {"summary": summary_match.group(1).replace('\\"', '"')}
        raise

def parse_json_array(text: str) -> list:
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    match = re.search(r"\[.*\]", clean, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array found in: {text[:200]}")
    return json.loads(match.group())

def check_texte(texte: str, endpoint: str):
    if not texte or len(texte.strip()) < 20:
        raise HTTPException(status_code=400, detail=f"{endpoint}: CV text too short.")


def _resolve_summary_inputs(req: EvalContextRequest) -> tuple[list[str], list[dict]]:
    """Normalise skills/experiences from payload; extracts from CV if absent."""
    skills: list[str] = []
    for s in req.skills or []:
        if isinstance(s, str) and s.strip():
            skills.append(s.strip())
    skills = _dedupe_skills(skills)

    experiences: list[dict] = []
    for e in req.experiences or []:
        if not isinstance(e, dict):
            continue
        experiences.append({
            "role": str(e.get("role") or e.get("Role") or "").strip(),
            "entreprise": str(e.get("entreprise") or e.get("Entreprise") or "").strip(),
            "years": str(e.get("years") or e.get("Years") or "").strip(),
            "summary": str(e.get("summary") or e.get("Summary") or "").strip(),
        })

    if skills or experiences:
        return skills, experiences

    if not req.texteExtrait:
        return [], []

    try:
        cv = preprocess_cv_text(req.texteExtrait)
        ner_payload = extract_raw(cv)
        seed = stable_seed(cv[:4000])
        skills = refine_skills(
            cv, call_groq, parse_json, MODEL_FAST, ner_payload=ner_payload, seed=seed
        )
        return skills, refine_experiences(
            cv, call_groq, parse_json, MODEL_LARGE, ner_payload=ner_payload
        )
    except Exception as exc:
        logger.warning("Auto-extract summary inputs failed: %s", exc)
        return [], []


def job_context(req) -> str:
    parts = []
    if getattr(req, 'titreOffre', None):
        parts.append(f"--- Job Title ---\n{req.titreOffre}")
    if getattr(req, 'description', None):
        parts.append(f"--- Job Description ---\n{req.description[:500]}")
    return "\n".join(parts)

def prepare_cv(text: str, max_chars: int = 4000) -> str:
    return clean_cv_text(text)[:max_chars]

def prepare_cv_with_sections(text: str, section_names: list, max_chars: int = 6000) -> str:
    cleaned = clean_cv_text(text)
    if len(cleaned) <= max_chars:
        return cleaned
    chunks: list[str] = []
    seen: set[str] = set()
    upper = text.upper()
    for name in section_names:
        idx = upper.find(name.upper())
        if idx < 0:
            continue
        chunk = clean_cv_text(text[idx:idx + 1800]).strip()
        if chunk and chunk not in seen:
            seen.add(chunk)
            chunks.append(chunk)
    if not chunks:
        return cleaned[:max_chars]
    combined = "\n\n".join([cleaned[: max_chars // 3]] + chunks)
    return combined[:max_chars]

def _normalize_cert_key(nom: str, organisme: Optional[str]) -> str:
    def norm(s: str) -> str:
        s = re.sub(r"[^\w\s]", "", (s or "").lower())
        s = re.sub(r"\s+", "", s)
        return s.strip()
    nom_base = (nom or "").split("|")[0].split(":")[0]
    return f"{norm(nom_base)}|{norm(organisme)}"

_SECTION_END = (
    r"(?i)\b(?:"
    r"EXPÉRIENCE|EXPERIENCES?|EXPERIENCE|WORK\s+EXPERIENCE|PROFESSIONAL\s+EXPERIENCE|"
    r"PROJETS?|PROJECTS?|COMPÉTENCES|COMPETENCES|SKILLS|"
    r"LANGUES|LANGUAGES|"
    r"CERTIFICATIONS?|CERTIFICATS?|CERTIFICATES?|"
    r"EDUCATION|ÉDUCATION|FORMATION|ÉTUDES|ACADEMIC\s+(?:BACKGROUND|QUALIFICATIONS?)|"
    r"INTERESTS?|REFERENCES?|PUBLICATIONS?|AWARDS?|HONORS?"
    r")\b"
)
_CERT_HEADERS = (
    r"(?i)\b(?:"
    r"CERTIFICATIONS?|CERTIFICATS?|CERTIFICATES?|"
    r"LICENCES?\s+ET\s+CERTIFICATIONS?|TRAINING\s+AND\s+CERTIFICATIONS?"
    r")\b"
)
_EDU_HEADERS = (
    r"(?i)\b(?:"
    r"EDUCATION|ÉDUCATION|FORMATION|ÉTUDES|FORMATIONS?|CURSUS|"
    r"ACADEMIC\s+(?:BACKGROUND|QUALIFICATIONS?)|SCOLARITÉ|SCOLARITE"
    r")\b"
)
_MONTHS = (
    r"(?:Janvier|F[eé]vrier|Mars|Avril|Mai|Juin|Juillet|Ao[uû]t|Septembre|Octobre|Novembre|D[eé]cembre|"
    r"January|February|March|April|May|June|July|August|September|October|November|December)"
)
_DEGREE_KEYWORDS = (
    r"(?i)\b(?:"
    r"engineering\s+degree|bachelor'?s?\s+degree|master'?s?\s+degree|associate\s+degree|"
    r"baccalaureate|baccalaur[eé]at|cycle\s+ing[eé]nieur|high\s+school|"
    r"ph\.?\s*d\.?|doctorate|doctorat|"
    r"dipl[oô]me(?:\s+d['\u2019\u0027]|\s+de|\s+national|\s+universitaire)?|"
    r"master|licence|bachelor|mba|bts|dut|deug|ing[eé]nieur"
    r")\b"
)
_SCHOOL_PATTERN = (
    r"(?i)\b("
    r"(?:Higher\s+)?Institute\s+[^,|•\ufffd]{3,120}|"
    r"(?:É|E|\uFFFD)?cole\s+[^,|•\ufffd]{3,120}|"
    r"Universit[yé]\s+[^,|•\ufffd]{3,120}|"
    r"Institut\s+[^,|•\ufffd]{3,120}|"
    r"Lyc[eé]e\s+[^,|•\ufffd]{3,80}|"
    r"(?:Mixed\s+)?High\s+School\s+[^,|•\ufffd]{3,80}|"
    r"[^,|•\ufffd]{3,80}\s+High\s+School\b|"
    r"Facult[yé]\s+[^,|•\ufffd]{3,120}|"
    r"School\s+[^,|•\ufffd]{3,120}|"
    r"College\s+[^,|•\ufffd]{3,120}"
    r")"
)

def _extract_section_block(text: str, header_pattern: str, max_chars: int = 3000) -> str:
    if not text:
        return ""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    block_lines: list[str] = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if not in_section:
            header_match = re.search(header_pattern, stripped)
            if header_match:
                in_section = True
                remainder = stripped[header_match.end():].strip()
                if remainder:
                    block_lines.append(remainder)
            continue
        if stripped and re.search(_SECTION_END, stripped) and block_lines:
            break
        if stripped:
            block_lines.append(stripped)
    if block_lines:
        return "\n".join(block_lines)[:max_chars]
    flat = re.sub(r"\s+", " ", text).strip()
    m = re.search(header_pattern, flat)
    if not m:
        return ""
    rest = flat[m.end():]
    end = re.search(_SECTION_END, rest)
    return (rest[: end.start()] if end else rest[:max_chars]).strip()

def _infer_issuer_from_name(nom: str) -> Optional[str]:
    patterns = [
        r"(?i)\b(?:with|from|by|de|par)\s+(Google\s+Cloud(?:\s+AI)?|AWS|Azure|NVIDIA|Cisco|Oracle|Microsoft|Udemy|Coursera|Simplilearn|LinkedIn\s+Learning|IBM|Meta|SAP)\b",
        r"(?i)\b(Google\s+Cloud(?:\s+AI)?|AWS|Azure|NVIDIA|Cisco|Oracle|Microsoft|Udemy|Coursera|Simplilearn|LinkedIn\s+Learning|IBM|Meta|SAP)\b",
        r"(?i)\b(SCRUM)\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, nom)
        if m:
            return m.group(1).strip()
    return None

def _parse_structured_cert_line(line: str) -> Optional[dict]:
    line = re.sub(r"^[\u2022\ufffd\u2023\*\-–]\s*", "", line.strip()).strip()
    if len(line) < 3:
        return None
    months = _MONTHS
    patterns = [
        rf"^(.+?)\s*[–—\-|]\s*(.+?)\s*\((?:{months}\s+)?(\d{{4}})\)\s*$",
        rf"^(.+?)\s*[–—\-|]\s*(.+?)\s*,\s*(\d{{4}})\s*$",
        rf"^(.+?)\s*\((?:{months}\s+)?(\d{{4}})\)\s*$",
        rf"^(.+?)\s*[–—\-|]\s*(.+?)\s*$",
    ]
    for i, pattern in enumerate(patterns):
        m = re.match(pattern, line, flags=re.IGNORECASE)
        if not m:
            continue
        groups = m.groups()
        if i == 2:
            return {"nom": groups[0].strip(), "organisme": _infer_issuer_from_name(groups[0]), "annee": groups[1], "type": "certification"}
        if i == 3 and len(groups[1].strip()) < 3:
            continue
        nom = groups[0].strip()
        org = groups[1].strip() if len(groups) > 1 and i != 2 else _infer_issuer_from_name(nom)
        year = groups[2] if len(groups) > 2 else None
        return {"nom": nom, "organisme": org, "annee": year, "type": "certification"}
    return None

def _is_valid_cert_line(line: str) -> bool:
    if len(line.strip()) < 3:
        return False
    if re.search(_CERT_HEADERS, line) or re.search(_SECTION_END, line):
        return False
    if re.match(r"^[\d\s/\-–—\.]+$", line):
        return False
    if re.match(r"(?i)^(email|phone|tel|linkedin|github|address|www\.|http)", line):
        return False
    return True

def _is_cert_section_boundary(line: str) -> bool:
    if re.match(r"(?i)^(PROJECTS?|PROJETS?|EXPERIENCE|EXPÉRIENCE|SKILLS|COMPÉTENCES|LANGUES|LANGUAGES)\b", line):
        return True
    if len(line) > 90 and not re.search(r"\(\d{4}\)", line) and not re.search(_CERT_HEADERS, line):
        return True
    return False

def extract_certifications_regex(text: str) -> list:
    block = _extract_section_block(text, _CERT_HEADERS)
    if not block:
        return []
    certs: list = []
    seen: set = set()
    def add_cert(entry: dict):
        nom = str(entry.get("nom", "")).strip()
        nom = re.sub(r"^[\u2022\ufffd\u2023\*\-–\s]+", "", nom).strip()
        if len(nom) < 3:
            return
        org = entry.get("organisme")
        org = str(org).strip() if org else _infer_issuer_from_name(nom)
        annee = entry.get("annee")
        annee = str(annee).strip() if annee else None
        key = _normalize_cert_key(nom, org)
        if key in seen:
            return
        seen.add(key)
        certs.append({"nom": nom, "organisme": org, "annee": annee, "type": "certification"})
    flat_lines: list[str] = []
    for line in block.split("\n"):
        line = line.strip()
        if _is_cert_section_boundary(line):
            break
        if line:
            flat_lines.append(line)
    flat = re.sub(r"\s+", " ", "\n".join(flat_lines)).strip()
    structured_pattern = rf"[\u2022\ufffd\u2023\*\-–]?\s*(.+?)\s*[–—\-|]\s*(.+?)\s*\((?:{_MONTHS}\s+)?(\d{{4}})\)"
    structured = re.findall(structured_pattern, flat, flags=re.IGNORECASE)
    if structured:
        for nom, org, year in structured:
            add_cert({"nom": nom, "organisme": org.strip(), "annee": year})
        return certs
    for line in block.split("\n"):
        line = line.strip()
        if _is_cert_section_boundary(line):
            break
        if not _is_valid_cert_line(line):
            continue
        parsed = _parse_structured_cert_line(line)
        if parsed:
            add_cert(parsed)
        elif 3 <= len(line) <= 150:
            add_cert({"nom": line, "organisme": _infer_issuer_from_name(line), "annee": None})
    return certs

def _parse_education_entry(raw_nom: str, raw_org: Optional[str], year: Optional[str]) -> Optional[dict]:
    nom = re.sub(r"\s+", " ", raw_nom).strip(" ,")
    nom = re.sub(r"^Actuellement\s+", "", nom, flags=re.IGNORECASE).strip()
    nom = re.sub(r"\s*\|\s*$", "", nom).strip()
    if len(nom) < 4:
        return None
    org = re.sub(r"\s+", " ", raw_org).strip(" ,") if raw_org else None
    return {"nom": nom, "organisme": org or None, "annee": year, "type": "diploma"}

def extract_education_regex(text: str) -> list:
    block = _extract_section_block(text, _EDU_HEADERS)
    if not block:
        return []
    diplomas: list = []
    seen: set = set()
    flat = re.sub(r"\s+", " ", block).strip()
    def add_diploma(entry: Optional[dict]):
        if not entry:
            return
        key = _normalize_cert_key(entry["nom"], entry.get("organisme"))
        if key in seen:
            return
        seen.add(key)
        diplomas.append(entry)
    colon_entries = list(re.finditer(_DEGREE_KEYWORDS + r"\s*:?", flat))
    if colon_entries:
        for i, dm in enumerate(colon_entries):
            next_start = colon_entries[i + 1].start() if i + 1 < len(colon_entries) else len(flat)
            segment = flat[dm.start():next_start].strip()
            year_m = re.search(
                r"((?:19|20)\d{2}\s*[-–—\uFFFD]\s*(?:19|20)\d{2})|((?:19|20)\d{4})\b",
                segment,
            )
            year = None
            content = segment
            if year_m:
                year = (year_m.group(1) or year_m.group(2)).replace(" ", "").replace("\uFFFD", "-")
                content = segment[:year_m.start()].strip(" ,")
            school_m = re.search(_SCHOOL_PATTERN, content)
            if school_m:
                org = school_m.group(1).strip()
                nom = content[:school_m.start()].strip(" ,")
            else:
                parts = [p.strip() for p in content.split(",") if p.strip()]
                if len(parts) >= 2:
                    nom = ", ".join(parts[:-1])
                    org = parts[-1]
                else:
                    nom = content.strip(" ,")
                    org = None
            add_diploma(_parse_education_entry(nom, org, year))
        if diplomas:
            return diplomas
    degree_starts = list(re.finditer(_DEGREE_KEYWORDS, flat))
    for i, dm in enumerate(degree_starts):
        prev = degree_starts[i - 1].start() if i > 0 else 0
        next_start = degree_starts[i + 1].start() if i + 1 < len(degree_starts) else len(flat)
        seg_start = max(prev, dm.start() - 120)
        segment = flat[seg_start:next_start].strip()
        deg_start = dm.start() - seg_start
        after_deg = segment[deg_start:]
        year_m = re.search(
            r"((?:19|20)\d{2}\s*[-–—\uFFFD]\s*(?:19|20)\d{2})|((?:19|20)\d{4})\b",
            after_deg,
        )
        year = None
        if year_m:
            year = (year_m.group(1) or year_m.group(2)).replace(" ", "").replace("\uFFFD", "-")
        school_m = re.search(_SCHOOL_PATTERN, after_deg)
        school_from_before = False
        if not school_m:
            before = segment[:deg_start].strip()
            school_m = re.search(_SCHOOL_PATTERN, before)
            school_from_before = bool(school_m)
        nom_end = len(after_deg)
        if school_m and not school_from_before:
            nom_end = min(nom_end, school_m.start())
        if year_m:
            nom_end = min(nom_end, year_m.start())
        nom = after_deg[:nom_end].strip()
        org = school_m.group(1).strip() if school_m else None
        add_diploma(_parse_education_entry(nom, org, year))
    return diplomas

def _infer_entry_type(nom: str, organisme: Optional[str]) -> str:
    text = f"{nom} {organisme or ''}".lower()
    diploma_keywords = [
        "baccalaur", "bachelor", "master", "licence", "doctorat", "doctorate", "phd", "ph.d",
        "cycle ingénieur", "cycle ingenieur", "engineering degree", "associate degree",
        "high school", "lycée", "lycee", "diplôme national", "diplome national", "bts", "dut", "deug", "mba",
    ]
    cert_keywords = [
        "certified", "certification", "certificate", "scrummaster", "scrum", "aws", "azure",
        "google cloud", "nvidia", "cisco", "pmp", "comptia", "udemy", "coursera", "simplilearn",
        "flutter", "deep learning", "big data", "blockchain", "block chain",
    ]
    if any(k in text for k in diploma_keywords) and not any(k in text for k in cert_keywords):
        return "diploma"
    return "certification"

def merge_certifications(*sources: list) -> list:
    merged: list = []
    by_nom: dict[str, int] = {}
    def nom_key(nom: str) -> str:
        base = (nom or "").split("|")[0].split(":")[0]
        return re.sub(r"[^\w]", "", base.lower())
    def score(entry: dict) -> int:
        s = 0
        if entry.get("organisme"):
            s += 2
        if entry.get("annee"):
            s += 1
        if entry.get("type") in ("certification", "diploma"):
            s += 1
        s += min(len(entry.get("nom", "")), 80) // 20
        return s
    for source in sources:
        for cert in source or []:
            if not isinstance(cert, dict):
                continue
            nom = str(cert.get("nom", "")).strip()
            if not nom:
                continue
            org = cert.get("organisme")
            org = str(org).strip() if org else None
            annee = cert.get("annee")
            annee = str(annee).strip() if annee else None
            entry_type = cert.get("type") or _infer_entry_type(nom, org)
            entry = {"nom": nom, "organisme": org, "annee": annee, "type": entry_type}
            key = nom_key(nom)
            if key in by_nom:
                idx = by_nom[key]
                if score(entry) > score(merged[idx]):
                    merged[idx] = entry
                continue
            by_nom[key] = len(merged)
            merged.append(entry)
    return merged

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
def health():
    return {
        "status": "ok",
        "version": "5.3.0",
        "model": MODEL_LARGE,
        "matching": "sentence-transformers + chroma + faiss",
    }


# =============================================================================
# 2. SCORE
# =============================================================================
@app.post("/ai/score")
def score(req: EvalRequest):
    check_texte(req.texteExtrait, "/ai/score")
    skills, experiences = _resolve_summary_inputs(req)
    try:
        return compute_match_score(
            cv_text=req.texteExtrait,
            skills=skills,
            experiences=experiences,
            titre_offre=req.titreOffre,
            description=req.description,
            type_contrat=req.typeContrat,
            candidate_id=req.candidatureId,
            offer_id=req.offreId,
        )
    except Exception as e:
        logger.exception("score failed")
        raise HTTPException(status_code=500, detail=f"Score error: {e}")


@app.post("/ai/rank-candidates")
def rank_candidates(req: RankCandidatesRequest):
    if not req.candidates:
        raise HTTPException(status_code=400, detail="candidates list is empty")
    try:
        ranked = rank_candidates_for_offer(
            titre_offre=req.titreOffre,
            description=req.description,
            candidates=req.candidates,
            type_contrat=req.typeContrat,
            top_k=req.topK,
        )
        return {"offreId": req.offreId, "ranked": ranked}
    except Exception as e:
        logger.exception("rank-candidates failed")
        raise HTTPException(status_code=500, detail=f"Rank error: {e}")


# ── Summary system prompt — ALWAYS English ─────────────────────────────────────
_SUMMARY_SYSTEM_EN = """\
You are a senior HR recruiter writing a concise, analytical narrative briefing about a candidate.
The summary MUST always be written in English, regardless of the CV language.

STRICT RULES:

R1. Write in fluent, natural English prose — NO JSON, NO bullet points, NO markdown.
    Sound like a real HR expert who has read both the CV and the job description carefully.

R2. Structure — exactly 3 sentences:

    SENTENCE 1 (Matching strengths):
    Start with: "The candidate's strongest relevant skills for this role include..."
    Mention ONLY skills/tools listed under "SKILLS MATCHING OFFER" or literally written in
    "EXTRACTED EXPERIENCES". Never infer or invent tools not present in those sections.
    If SKILLS MATCHING OFFER is NONE, state limited direct match and describe the actual
    background from experiences without inventing technologies.

    SENTENCE 2 (Gaps — ONLY when Confirmed MISSING is not empty):
    Start with: "However, key missing skills that limit their fit include..."
    List ONLY requirements from the "Confirmed MISSING" section in the data below.
    A technology present in the candidate's skills OR experience descriptions is NOT a gap.
    If Confirmed MISSING is NONE/empty, SKIP Sentence 2 entirely — go straight to Sentence 3.

    SENTENCE 3 (Recommendation):
    Use this exact format:
    "Based on a [weak/partial/strong] overall fit ([X]% of requirements covered) for the
    role «[ROLE TITLE]», I recommend [rejecting/considering with caution/advancing] this candidate."
    — weak fit → rejecting
    — partial fit → considering with caution
    — strong fit → advancing
    Use the EXACT fit score and label from the data provided. Never invent a different number.

R3. NEVER mention cosine, embeddings, sentence-transformers, or any technical labels.
R4. NEVER use bullet points, headers, or JSON in your response.
R5. NEVER write in French or any language other than English.
R6. Output plain text only — 3 sentences, nothing else.
R7. Sentence 2 must cite ONLY "Confirmed MISSING" items from the data. Never invent gaps.
    Tools mentioned in experiences are present — never report them as missing.
R8. Do NOT start with the candidate's last role/job title — start directly with the skills analysis.
R9. NEVER hallucinate skills or tools. Every technology named must appear
    verbatim in SKILLS MATCHING OFFER or EXTRACTED EXPERIENCES.\
"""


def _build_summary_prompt(
    enriched_context: str,
    has_offer: bool,
    ctx: dict,
    skills: list,
    experiences: list,
    titre_offre: str,
    description: str,
) -> str:
    """Build LLM prompt from pipeline context — gaps must match skills + experiences."""
    gaps = ctx.get("skill_gaps", {})
    fit_score = gaps.get("fit_score", 0)
    fit_label = gaps.get("fit_label", "unknown")
    offer_title = ctx.get("offer_title") or titre_offre or "this role"

    if has_offer:
        fit_label_display = {"strong": "strong", "partial": "partial", "weak": "weak"}.get(
            fit_label, fit_label
        )
        prompt = (
            f"⚠ LOCKED FIT SCORE (use verbatim in Sentence 3 — do NOT recalculate): "
            f"{fit_score}% — {fit_label_display}\n"
            f"⚠ ROLE: {offer_title}\n\n"
            f"Write exactly 3 sentences following rules R1–R8.\n\n"
            f"=== JOB DESCRIPTION ===\n"
            f"{_strip_html(description or '')[:1500] if description else 'not provided'}\n\n"
            f"{format_context_for_prompt(ctx, compact=False)}\n\n"
            "INSTRUCTIONS:\n"
            "- Sentence 1: ONLY skills from SKILLS MATCHING OFFER or EXTRACTED EXPERIENCES.\n"
            "- Sentence 2: cite ONLY items under 'Confirmed MISSING'. Skip Sentence 2 if NONE.\n"
            "- Never invent tools or technologies not explicitly listed above.\n"
            "Respond with plain text only."
        )
    else:
        prompt = (
            f"Write a 2–3 sentence professional summary in English of this candidate "
            f"(no job offer provided).\n\n"
            f"{format_context_for_prompt(ctx, compact=False)}"
        )

    return prompt


# ── Endpoint /ai/summarize ─────────────────────────────────────────────────────
@app.post("/ai/summarize")
def summarize(req: EvalRequest):
    check_texte(req.texteExtrait, "/ai/summarize")

    skills, experiences = _resolve_summary_inputs(req)
    if not skills and not experiences:
        raise HTTPException(
            status_code=400,
            detail="No skills or experience extracted. Please run Extract Skills / Extract Experience first.",
        )

    try:
        ctx = build_summary_context(
            skills=skills,
            experiences=experiences,
            titre_offre=req.titreOffre,
            description=req.description,
            type_contrat=req.typeContrat,
        )
    except Exception as e:
        logger.exception("build_summary_context failed")
        raise HTTPException(status_code=500, detail=f"Summary context error: {e}")

    has_offer = ctx["has_offer"]

    # Build prompt with raw skills + job description for accurate LLM gap analysis
    prompt = _build_summary_prompt(
        enriched_context="",
        has_offer=has_offer,
        ctx=ctx,
        skills=skills,
        experiences=experiences,
        titre_offre=req.titreOffre or "",
        description=req.description or "",
    )

    seed_input = (
        "summary-v2::"
        + (req.texteExtrait or "")[:500]
        + "||" + (req.titreOffre or "")
        + "||" + (req.description or "")[:500]
        + "||" + str(ctx.get("skill_gaps", {}).get("fit_score", 0))
    )

    try:
        seed = stable_seed(seed_input)
        raw = call_groq(
            prompt,
            max_tokens=450 if has_offer else 250,
            model=MODEL_LARGE,   # Use the large model for better gap reasoning
            system=_SUMMARY_SYSTEM_EN,
            seed=seed,
        )

        summary = raw.strip()

        # Defense: if LLM returns JSON anyway, extract the text
        if summary.lstrip().startswith("{"):
            try:
                import json as _json
                parsed = _json.loads(summary)
                summary = parsed.get("summary") or parsed.get("text") or ""
            except Exception:
                m = re.search(r'"(?:summary|text)"\s*:\s*"(.+?)"\s*}', summary, re.DOTALL)
                summary = m.group(1).replace('\\"', '"') if m else summary

        # Strip residual markdown
        summary = re.sub(r"^#+\s+", "", summary, flags=re.MULTILINE)
        summary = re.sub(r"\*\*(.+?)\*\*", r"\1", summary)
        summary = re.sub(r"\*(.+?)\*", r"\1", summary)
        summary = summary.strip()

        if not summary or len(summary) < 30:
            raise ValueError("Empty or too short summary from LLM")

        return {"summary": summary}

    except Exception as e:
        logger.warning("summarize LLM failed, fallback to compose_summary: %s", e)
        return {"summary": compose_summary(ctx)}


# =============================================================================
# 4. SKILLS EXTRACTION
# =============================================================================
@app.post("/ai/extract-skills")
def extract_skills(req: CvRequest):
    check_texte(req.texteExtrait, "/ai/extract-skills")
    text = preprocess_cv_text(req.texteExtrait)
    try:
        ner_payload = extract_raw(text)
        seed = stable_seed(text[:4000])
        skills = refine_skills(
            text, call_groq, parse_json, MODEL_FAST,
            ner_payload=ner_payload, seed=seed,
        )
        return {"skills": _dedupe_skills(skills)}
    except Exception as e:
        logger.error("RoBERTa NER skills extraction failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Skills extraction error: {e}")

# =============================================================================
# 5. EXPERIENCE EXTRACTION
# =============================================================================
@app.post("/ai/extract-experience")
def extract_experience(req: CvRequest):
    check_texte(req.texteExtrait, "/ai/extract-experience")
    text = preprocess_cv_text(req.texteExtrait)
    try:
        ner_payload = extract_raw(text)
        experiences = refine_experiences(
            text, call_groq, parse_json, MODEL_LARGE, ner_payload=ner_payload
        )
        return {"experiences": experiences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Experience error: {e}")

# =============================================================================
# 6. CERTIFICATIONS EXTRACTION
# =============================================================================
@app.post("/ai/extract-certifications")
def extract_certifications(req: CvRequest):
    check_texte(req.texteExtrait, "/ai/extract-certifications")
    try:
        ner_payload = extract_raw(req.texteExtrait)
        certifications = refine_certifications(
            req.texteExtrait, call_groq, parse_json, MODEL_LARGE, ner_payload=ner_payload
        )
        return {"certifications": certifications}
    except Exception as e:
        logger.error("RoBERTa NER certifications extraction failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Certifications error: {e}")

# =============================================================================
# 7. COMPANIES EXTRACTION
# =============================================================================
@app.post("/ai/extract-companies")
def extract_companies(req: CvRequest):
    check_texte(req.texteExtrait, "/ai/extract-companies")
    try:
        ner_payload = extract_raw(req.texteExtrait)
        companies = refine_companies(
            req.texteExtrait, call_groq, parse_json, MODEL_FAST, ner_payload=ner_payload
        )
        return {"companies": companies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Companies error: {e}")

# =============================================================================
# 8. INTERVIEW QUESTIONS GENERATION
# =============================================================================
@app.post("/ai/interview-questions")
def generate_interview_questions(req: InterviewQuestionsRequest):
    n = min(max(req.nombreQuestions or 8, 4), 12)
    skills_str = ", ".join(req.competences) if req.competences else "non spécifiées"
    prompt = f"""Tu es un recruteur expert. Génère exactement {n} questions d'entretien professionnelles
pour le poste suivant. Les questions doivent être pertinentes, progressives (du général au technique),
et adaptées au profil du candidat.

STRUCTURE DES QUESTIONS (répartition suggérée pour {n} questions) :
- 1-2 questions d'introduction (présentation, motivation)
- 2-3 questions techniques sur les compétences du poste
- 1-2 questions comportementales (STAR method)
- 1-2 questions de mise en situation / cas pratique
- 1 question sur les perspectives (projets, évolution)

POSTE : {req.titreOffre}
DESCRIPTION : {(req.descriptionOffre or 'Non fournie')[:500]}
COMPÉTENCES CV : {skills_str}
RÉSUMÉ CV : {(req.cvResume or 'Non fourni')[:300]}

Réponds UNIQUEMENT avec ce JSON (pas de markdown) :
{{
  "questions": [
    {{
      "id": 1,
      "texte": "Question complète ici ?",
      "type": "introduction|technique|comportementale|situation|perspective",
      "dureeEstimee": 120,
      "mots_cles": ["mot1", "mot2"]
    }}
  ]
}}"""
    try:
        raw = call_groq(prompt, max_tokens=2000)
        result = parse_json(raw)
        if not isinstance(result.get("questions"), list):
            raise ValueError("No questions array")
        questions = []
        for i, q in enumerate(result["questions"]):
            if isinstance(q, dict) and q.get("texte"):
                questions.append({
                    "id": i + 1,
                    "texte": str(q.get("texte","")).strip(),
                    "type": str(q.get("type","technique")).strip(),
                    "dureeEstimee": int(q.get("dureeEstimee", 120)),
                    "mots_cles": q.get("mots_cles", [])
                })
        return {"questions": questions, "total": len(questions), "titreOffre": req.titreOffre}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview questions error: {e}")

# =============================================================================
# 9. ANSWER EVALUATION
# =============================================================================
@app.post("/ai/evaluate-answer")
def evaluate_answer(req: EvaluateAnswerRequest):
    if not req.reponse or len(req.reponse.strip()) < 5:
        return {"score": 0, "feedback": "Pas de réponse fournie.", "points_forts": [], "points_amelioration": []}
    prompt = f"""Tu es un expert RH. Évalue cette réponse de candidat à une question d'entretien.

POSTE : {req.titreOffre or 'Non spécifié'}
QUESTION : {req.question}
RÉPONSE DU CANDIDAT : {req.reponse[:1000]}

CRITÈRES D'ÉVALUATION :
- Pertinence par rapport à la question (0-30 pts)
- Clarté et structure de la réponse (0-20 pts)
- Profondeur technique / expertise démontrée (0-30 pts)
- Communication et expression (0-20 pts)

Réponds UNIQUEMENT avec ce JSON :
{{
  "score": <entier 0-100>,
  "niveau": "excellent|bon|moyen|insuffisant",
  "feedback": "Feedback constructif en 1-2 phrases",
  "points_forts": ["point1", "point2"],
  "points_amelioration": ["point1"],
  "reponse_ideale_hint": "Direction vers une meilleure réponse en 1 phrase"
}}"""
    try:
        raw = call_groq(prompt, max_tokens=400)
        result = parse_json(raw)
        result["score"] = max(0, min(100, int(float(result.get("score", 50)))))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluate answer error: {e}")

# =============================================================================
# 10. INTERVIEW REPORT GENERATION
# =============================================================================
@app.post("/ai/generate-report")
def generate_report(req: GenerateReportRequest):
    if not req.questions:
        raise HTTPException(status_code=400, detail="Questions list is required")
    qa_summary = ""
    total_score = 0
    count = 0
    for q in req.questions:
        if q.get("reponse") and q.get("score") is not None:
            qa_summary += f"\nQ{q.get('id','')}: {q.get('texte','')}\n"
            qa_summary += f"Réponse: {str(q.get('reponse',''))[:200]}\n"
            qa_summary += f"Score: {q.get('score')}/100\n"
            total_score += int(q.get("score", 0))
            count += 1
    avg_score = round(total_score / count) if count > 0 else 0
    prompt = f"""Tu es un expert RH. Génère un rapport d'entretien professionnel et objectif.

CANDIDAT : {req.nomCandidat}
POSTE : {req.titreOffre}
DURÉE : {req.dureeMinutes} minutes
SCORE MOYEN : {avg_score}/100
QUESTIONS ET RÉPONSES :
{qa_summary[:3000]}

Réponds UNIQUEMENT avec ce JSON :
{{
  "scoreGlobal": {avg_score},
  "mention": "Excellent|Bien|Satisfaisant|Insuffisant",
  "resume_executif": "Résumé objectif de l'entretien en 3-4 phrases",
  "points_forts": ["point1", "point2", "point3"],
  "points_amelioration": ["point1", "point2"],
  "recommandation": "Recruter|À considérer|Refuser",
  "commentaire_recruteur": "Commentaire détaillé pour le recruteur en 2-3 phrases",
  "competences_evaluees": [
    {{"competence": "nom", "niveau": "Expert|Avancé|Intermédiaire|Débutant", "score": 85}}
  ]
}}"""
    try:
        raw = call_groq(prompt, max_tokens=1000)
        result = parse_json(raw)
        result["scoreGlobal"] = avg_score
        result["nomCandidat"] = req.nomCandidat
        result["titreOffre"] = req.titreOffre
        result["dureeMinutes"] = req.dureeMinutes
        result["nbQuestionsRepondues"] = count
        result["dateEntretien"] = ""
        result["verificationFacialeOk"] = req.verificationFacialeOk

        fraud_feats = req.fraudMetrics.model_dump() if req.fraudMetrics else {}
        if req.verificationFacialeOk is False and not fraud_feats.get("no_face_count"):
            fraud_feats["no_face_count"] = 1
        try:
            fraud_result = predict_fraud(fraud_feats or None)
            result["fraudDetection"] = fraud_result
            result["nbChangementsOnglet"] = int(fraud_feats.get("tab_changes", 0))
        except Exception as fraud_exc:
            logger.warning("Fraud prediction failed: %s", fraud_exc)
            result["fraudDetection"] = None
            result["nbChangementsOnglet"] = int(fraud_feats.get("tab_changes", 0))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generate report error: {e}")

# =============================================================================
# 11. QUIZ GENERATION
# =============================================================================
@app.post("/ai/generate-quiz")
def generate_quiz_for_offer(req: GenerateQuizRequest):
    try:
        num = max(3, min(req.num_questions, 20))
        prompt = f"""You are an expert technical recruiter and quiz designer.
Generate {num} multiple-choice questions to assess a candidate for this job offer.

Job Title: {req.titreOffre}
Job Description: {(req.description or "")[:1000]}

REQUIREMENTS:
- Questions MUST be directly related to the skills, technologies, and responsibilities of this job offer
- Each question has EXACTLY 3 answer choices
- Exactly ONE correct answer per question
- All text in English
- Difficulty: mix of easy (30%), medium (50%), hard (20%)

Respond with ONLY valid JSON, no explanation, no markdown:
{{
  "questions": [
    {{
      "question": "<specific technical question>",
      "choices": ["<option A>", "<option B>", "<option C>"],
      "correct_index": <0|1|2>
    }}
  ]
}}"""
        raw = call_groq(prompt, max_tokens=2000)
        try:
            data = parse_json(raw)
        except Exception:
            match = re.search(r'\{.*"questions".*\}', raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                return {"questions": []}
        questions_raw = data.get("questions", [])
        questions = []
        for idx, q in enumerate(questions_raw[:num]):
            choices = q.get("choices", [])
            if len(choices) < 3:
                choices += ["—"] * (3 - len(choices))
            questions.append({
                "id":            idx + 1,
                "question":      q.get("question", ""),
                "choices":       choices[:3],
                "correct_index": int(q.get("correct_index", 0)) % 3,
            })
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz error: {e}")