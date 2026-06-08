"""FraudPredictor v5 — XGBoost pipeline for virtual interview proctoring."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np

logger = logging.getLogger("recruit-ai")

_MODEL_PATH = Path(__file__).resolve().parent / "models" / "fraud_predictor_v5.joblib"
_CONFIG_PATH = Path(__file__).resolve().parent / "models" / "fraud_config_v5.json"

_model = None
_config: Optional[dict] = None
_load_error: Optional[str] = None

DEFAULT_FEATURES: dict[str, float] = {
    "tab_changes": 0,
    "window_blurs": 0,
    "no_face_count": 0,
    "multi_face_count": 0,
    "face_absence_ratio": 0.0,
    "gaze_away_count": 0,
    "gaze_away_ratio": 0.0,
    "phone_detected": 0,
    "book_detected": 0,
    "laptop_detected": 0,
    "extra_person": 0,
    "suspicious_obj_count": 0,
    "answer_delay": 1.5,
    "answer_speed": 2.0,
    "frontend_fraud_score": 0.05,
}


def _load() -> tuple[Any, dict]:
    global _model, _config, _load_error
    if _model is not None and _config is not None:
        return _model, _config
    if _load_error:
        raise RuntimeError(_load_error)
    try:
        if not _MODEL_PATH.is_file():
            raise FileNotFoundError(f"Fraud model not found: {_MODEL_PATH}")
        if not _CONFIG_PATH.is_file():
            raise FileNotFoundError(f"Fraud config not found: {_CONFIG_PATH}")
        _model = joblib.load(_MODEL_PATH)
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            _config = json.load(f)
        logger.info("Loaded FraudPredictor v5 from %s", _MODEL_PATH)
        return _model, _config
    except Exception as exc:
        _load_error = str(exc)
        logger.error("Failed to load fraud model: %s", exc)
        raise


def _normalize_for_model(feats: dict, config: dict) -> dict:
    """
    Ramène les comptages à l'échelle du dataset d'entraînement (~35 observations / entretien).
    Sans cela, un scan caméra chaque seconde gonfle les counts et fausse le XGBoost.
    """
    ref = float(config.get("reference_observations", 35))
    checks = max(float(feats.get("face_checks", 0)), 1.0)
    scale = ref / checks
    out = dict(feats)

    for key in ("no_face_count", "gaze_away_count"):
        raw = float(out.get(key, 0))
        out[key] = float(min(round(raw * scale), ref))

    mfc = float(out.get("multi_face_count", 0))
    out["multi_face_count"] = float(min(round(mfc * scale), 5))

    soc = float(out.get("suspicious_obj_count", 0))
    out["suspicious_obj_count"] = float(min(soc, 5))

    # Ratios inchangés ; phone/extra_person déjà 0/1
    return out


def _rule_score_and_violations(feats: dict[str, float]) -> tuple[float, list[str]]:
    """Score explicite 0–100 basé sur les comportements observés (complète le ML)."""
    score = 0.0
    viols: list[str] = []

    phone_hits = int(feats.get("phone_likely_count", 0))
    if feats.get("phone_detected", 0) >= 1 or phone_hits >= 2:
        score = max(score, 72.0 + min(phone_hits, 10) * 2.0)
        viols.append("Telephone detecte")

    far = float(feats.get("face_absence_ratio", 0))
    if far > 0.35:
        score = max(score, 45.0 + far * 50.0)
        viols.append("Absence visage > 35%")
    elif far > 0.15:
        score = max(score, 30.0 + far * 45.0)
        viols.append("Visage souvent absent")

    gar = float(feats.get("gaze_away_ratio", 0))
    ghr = float(feats.get("gaze_horizontal_ratio", 0))
    ghc = int(feats.get("gaze_horizontal_count", 0))

    if ghr > 0.08 or ghc >= 2:
        score = max(score, 32.0 + max(ghr, 0.08) * 40.0)
        viols.append("Regard detourne sur le cote")
    elif gar > 0.12 or ghc >= 4:
        score = max(score, 35.0 + gar * 45.0)
        viols.append("Regard detourne frequent")
    elif gar > 0.06 or ghc >= 1:
        score = max(score, 26.0 + gar * 35.0)
        if not any("Regard" in v for v in viols):
            viols.append("Regard instable")

    partial = int(feats.get("face_partial_count", 0))
    if partial >= 4:
        score = max(score, 42.0)
        viols.append("Visage partiellement masque")

    if feats.get("multi_face_count", 0) >= 2:
        score = max(score, 65.0)
        viols.append("Multi-visages")

    if feats.get("extra_person", 0) >= 1:
        score = max(score, 70.0)
        viols.append("Personne supplementaire")

    if feats.get("tab_changes", 0) >= 6:
        score = max(score, 52.0)
        viols.append("Changements d'onglet excessifs")
    elif feats.get("tab_changes", 0) >= 3:
        score = max(score, 32.0)
        viols.append("Changements d'onglet repetes")

    soc = int(feats.get("suspicious_obj_count", 0))
    if soc >= 5:
        score = max(score, 55.0)
        viols.append("Comportements suspects repetes")

    ffs = float(feats.get("frontend_fraud_score", 0.05))
    if ffs >= 0.35:
        score = max(score, ffs * 100.0)

    # Combinaison de signaux : fraude délibérée = score plus sévère
    if len(viols) >= 3:
        score = max(score, 72.0)
    elif len(viols) >= 2:
        score = max(score, 58.0)

    return round(min(score, 99.0), 1), viols


def predict_candidate(features_override: Optional[dict] = None, threshold: Optional[float] = None) -> dict:
    """Prédit la suspicion ; combine XGBoost + règles explicites."""
    model, config = _load()
    feature_names = config["feature_names"]
    optimal_t = float(config.get("optimal_threshold", 0.31))
    t = float(threshold) if threshold is not None else optimal_t

    feats = {**DEFAULT_FEATURES, **(features_override or {})}
    raw_feats = dict(feats)
    ml_feats = _normalize_for_model(feats, config)

    vec = np.array([[float(ml_feats[k]) for k in feature_names]], dtype=np.float32)
    ml_proba = float(model.predict_proba(vec)[0, 1])
    ml_score = round(ml_proba * 100, 1)

    rule_score, rule_viols = _rule_score_and_violations(raw_feats)
    final_score = round(max(ml_score, rule_score), 1)
    final_proba = final_score / 100.0
    is_suspect = final_proba >= t or final_score >= 40.0 or len(rule_viols) >= 2

    if final_score >= 70:
        level, icon = "ELEVE", "🔴"
    elif final_score >= 50:
        level, icon = "MOYEN", "🟠"
    elif final_score >= 30:
        level, icon = "FAIBLE", "🟡"
    else:
        level, icon = "AUCUN", "🟢"

    return {
        "verdict": "SUSPECT" if is_suspect else "NON SUSPECT",
        "score": final_score,
        "ml_score": ml_score,
        "rule_score": rule_score,
        "proba_suspect": round(final_proba, 4),
        "ml_proba_suspect": round(ml_proba, 4),
        "threshold": round(t, 2),
        "level": level,
        "icon": icon,
        "is_suspect": is_suspect,
        "viols": rule_viols,
        "model_version": config.get("version", "v5"),
        "features_used": {k: ml_feats[k] for k in feature_names},
        "features_raw": {k: raw_feats[k] for k in feature_names if k in raw_feats},
        "proctoring_detail": {
            k: raw_feats[k]
            for k in (
                "face_absence_ratio", "gaze_away_ratio", "gaze_horizontal_ratio",
                "gaze_horizontal_count",
                "phone_detected", "phone_likely_count", "face_partial_count",
                "suspicious_obj_count", "face_checks",
            )
            if k in raw_feats
        },
    }
