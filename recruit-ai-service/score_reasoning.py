"""
Niveau 4 — LLM Reasoning Score (Groq / Llama).
Évalue cohérence, expertise, pertinence et adéquation métier.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Optional

import httpx
from groq import Groq

logger = logging.getLogger("recruit-ai")

_MODEL = os.getenv("MODEL_SCORE_REASONING", "llama-3.1-8b-instant")
_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY manquante")
        _client = Groq(api_key=key, timeout=httpx.Timeout(90.0, connect=30.0))
    return _client


def _parse_json(text: str) -> dict:
    clean = re.sub(r"```(?:json)?", "", text or "").replace("```", "").strip()
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if not match:
        raise ValueError("No JSON in LLM response")
    return json.loads(match.group())


def _clamp_score(v) -> int:
    try:
        n = int(round(float(v)))
    except (TypeError, ValueError):
        n = 50
    return max(0, min(100, n))


def fetch_llm_reasoning_score(
    titre_offre: Optional[str],
    description: Optional[str],
    type_contrat: Optional[str],
    candidate_profile: str,
    skill_summary: str,
    semantic_score: int,
    skill_score: int,
    experience_score: int,
) -> dict:
    """
    Retourne technical_fit, experience_fit, domain_fit, overall_reasoning_score, reasoning (court).
    """
    prompt = f"""Evaluate how well this candidate matches the job offer. Act as a senior technical recruiter.

JOB
Title: {titre_offre or "N/A"}
Contract: {type_contrat or "N/A"}
Description (excerpt): {(description or "")[:1200]}

CANDIDATE PROFILE
{candidate_profile[:2000]}

SKILL MATCH ANALYSIS
{skill_summary[:1500]}

AUTOMATED SIGNALS (0-100, for context only)
- semantic_similarity: {semantic_score}
- skill_match: {skill_score}
- experience_match: {experience_score}

Respond with JSON only:
{{
  "technical_fit": <0-100, skills & tools vs offer>,
  "experience_fit": <0-100, relevant projects/internships/depth>,
  "domain_fit": <0-100, job title/role/field alignment — LOW if candidate role differs from offer (e.g. student profile vs senior hire)>,
  "overall_reasoning_score": <0-100, holistic hire potential>,
  "reasoning": "<2 short sentences in English>"
}}"""

    system = (
        "You are a senior recruiter. Output valid JSON only. "
        "For domain_fit: use semantic alignment between job title, candidate roles, and profile. "
        "Give HIGH domain_fit when title and candidate background clearly align; "
        "give LOW domain_fit when the offered role level or function clearly diverges from the profile. "
        "For experience_fit: value internships, personal projects and hands-on work when they semantically match the offer. "
        "A student with several relevant projects/internships should not score low on experience for an internship role."
    )

    try:
        response = _get_client().chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.25,
            max_tokens=400,
        )
        raw = (response.choices[0].message.content or "").strip()
        data = _parse_json(raw)
    except Exception as e:
        logger.warning("LLM reasoning score failed: %s", e)
        return _fallback_llm_scores(semantic_score, skill_score, experience_score)

    overall = _clamp_score(
        data.get("overall_reasoning_score")
        or data.get("overall_score")
        or (semantic_score + skill_score + experience_score) / 3
    )
    return {
        "technical_fit": _clamp_score(data.get("technical_fit", skill_score)),
        "experience_fit": _clamp_score(data.get("experience_fit", experience_score)),
        "domain_fit": _clamp_score(data.get("domain_fit", semantic_score)),
        "overall_reasoning_score": overall,
        "reasoning": str(data.get("reasoning") or "")[:500],
        "source": "llm",
    }


def _fallback_llm_scores(semantic: int, skill: int, experience: int) -> dict:
    overall = int(round(0.35 * semantic + 0.40 * skill + 0.25 * experience))
    overall = max(0, min(100, overall))
    return {
        "technical_fit": skill,
        "experience_fit": experience,
        "domain_fit": semantic,
        "overall_reasoning_score": overall,
        "reasoning": "LLM unavailable; scores derived from semantic and skill matching.",
        "source": "fallback",
    }
