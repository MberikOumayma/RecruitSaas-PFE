"""spaCy RoBERTa NER — raw entity extraction only (no heuristics)."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

# Avoid CUDA init attempts on machines without a GPU (spaCy/thinc still runs on CPU).
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

logger = logging.getLogger("recruit-ai")

_MODEL_DIR = Path(__file__).resolve().parent / "models" / "cv_ner_roberta_best"
_nlp = None
_load_error: Optional[str] = None

Entity = dict[str, object]

NER_LABELS = (
    "SKILL",
    "JOB_TITLE",
    "COMPANY",
    "DATE",
    "EXPERIENCE_DESC",
    "DEGREE",
    "INSTITUTION",
    "CERTIFICATION",
)


def _ensure_cfg_files(model_dir: Path) -> None:
    for sub in ("ner", "transformer"):
        cfg_txt = model_dir / sub / "cfg.txt"
        cfg = model_dir / sub / "cfg"
        if cfg_txt.is_file() and not cfg.is_file():
            cfg.write_text(cfg_txt.read_text(encoding="utf-8"), encoding="utf-8")


def get_nlp():
    global _nlp, _load_error
    if _nlp is not None:
        return _nlp
    if _load_error:
        raise RuntimeError(_load_error)
    try:
        import spacy

        try:
            import spacy_transformers  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "spacy-transformers is not installed. "
                "Use: py -3.12 -m pip install -r requirements.txt "
                "then: py -3.12 -m uvicorn main:app --reload"
            ) from exc

        if not _MODEL_DIR.is_dir():
            raise FileNotFoundError(f"NER model directory not found: {_MODEL_DIR}")
        _ensure_cfg_files(_MODEL_DIR)
        logger.info("Loading spaCy NER model from %s", _MODEL_DIR)
        _nlp = spacy.load(_MODEL_DIR)
        return _nlp
    except Exception as exc:
        _load_error = str(exc)
        logger.error("Failed to load spaCy NER model: %s", exc)
        raise


def run_ner(text: str) -> list[Entity]:
    nlp = get_nlp()
    doc = nlp(text)
    return [
        {
            "label": ent.label_,
            "text": ent.text.strip(),
            "start": ent.start_char,
            "end": ent.end_char,
        }
        for ent in doc.ents
        if ent.text.strip()
    ]


def entities_by_label(entities: list[Entity]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {label: [] for label in NER_LABELS}
    for ent in entities:
        label = str(ent["label"])
        if label not in grouped:
            grouped[label] = []
        grouped[label].append({
            "text": ent["text"],
            "start": ent["start"],
            "end": ent["end"],
        })
    return grouped


def extract_raw(text: str) -> dict:
    """Run RoBERTa NER and return raw entities grouped by label."""
    cleaned = (text or "").strip()
    if len(cleaned) < 20:
        return {"entities": [], "by_label": entities_by_label([])}

    entities = run_ner(cleaned)
    return {
        "entities": entities,
        "by_label": entities_by_label(entities),
    }


def format_entities_for_prompt(by_label: dict[str, list[dict]]) -> str:
    compact = {k: v for k, v in by_label.items() if v}
    return json.dumps(compact, ensure_ascii=False, indent=2)
