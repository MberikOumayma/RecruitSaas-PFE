"""Sanity checks for pure Python helpers (no ML models)."""

import os

os.environ.setdefault("GROQ_API_KEY", "test-key-for-ci")

from main import clean_cv_text, parse_json_array, stable_seed


def test_stable_seed_is_deterministic():
    assert stable_seed("same-input") == stable_seed("same-input")
    assert stable_seed("a") != stable_seed("b")


def test_clean_cv_text_adds_spaces_between_words_and_digits():
    result = clean_cv_text("VueJS2024")
    assert " " in result


def test_parse_json_array_extracts_array_from_markdown():
    raw = 'Here is the result:\n```json\n["Python", "Docker"]\n```'
    assert parse_json_array(raw) == ["Python", "Docker"]
