"""
CV text preparation (OCR/PDF extracted text) before NER.

Goal: improve robustness without modifying the NER pipeline code.
This script takes raw extracted text and outputs a cleaned version:
- Unicode normalization (NFKC)
- whitespace normalization (preserve newlines)
- de-hyphenation across line breaks (e.g. "inter-\n national" -> "international")
- remove obvious OCR noise lines
- remove repeated identical header/footer lines

Usage:
  py -3.12 preprocess_cv_text.py --in raw.txt --out cleaned.txt
  py -3.12 preprocess_cv_text.py --in raw.txt --stdout
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from collections import Counter


_WS_RE = re.compile(r"[ \t\r\f\v]+")
_ONLY_PUNCT_RE = re.compile(r"^[\W_]+$", re.UNICODE)
_PAGE_MARKER_RE = re.compile(r"^\s*(page|p\.)\s*\d+\s*(/|sur)?\s*\d*\s*$", re.IGNORECASE)


def _normalize_unicode(text: str) -> str:
    text = text.replace("\ufeff", "")  # BOM
    # common non-breaking spaces → normal space
    text = text.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2007", " ")
    return unicodedata.normalize("NFKC", text)


def _normalize_whitespace_keep_newlines(text: str) -> str:
    # Normalize line endings first
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for ln in text.split("\n"):
        ln = _WS_RE.sub(" ", ln).strip()
        lines.append(ln)
    # keep blank lines but collapse large runs later
    out = "\n".join(lines)
    out = re.sub(r"\n{4,}", "\n\n\n", out)
    return out.strip()


def _dehyphenate_linebreaks(text: str) -> str:
    # Join hyphenated words split across lines: "... inter-\n national" → "international"
    # Keep cases where hyphen is meaningful (e.g., "C++-like") by requiring letters.
    text = re.sub(r"([A-Za-zÀ-ÖØ-öø-ÿ])-\n([A-Za-zÀ-ÖØ-öø-ÿ])", r"\1\2", text)
    return text


def _drop_obvious_noise_lines(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    for ln in lines:
        if not ln:
            cleaned.append("")
            continue

        # very short pure punctuation separators: "----", "___", "|||"
        if len(ln) <= 6 and _ONLY_PUNCT_RE.match(ln):
            continue

        # OCR garbage lines: many pipes/underscores, or mostly non-alnum
        alnum = sum(ch.isalnum() for ch in ln)
        if len(ln) >= 10 and alnum / max(len(ln), 1) < 0.18:
            # keep if it contains an email/phone-like signal
            if "@" in ln or re.search(r"\+?\d[\d\s().-]{6,}\d", ln):
                cleaned.append(ln)
            else:
                continue

        # repeated page markers
        if _PAGE_MARKER_RE.match(ln):
            continue

        cleaned.append(ln)

    # collapse multiple blanks
    out: list[str] = []
    blank_run = 0
    for ln in cleaned:
        if ln == "":
            blank_run += 1
            if blank_run <= 2:
                out.append("")
        else:
            blank_run = 0
            out.append(ln)
    return out


def _dedupe_repeated_lines(lines: list[str], *, min_len: int = 18, min_count: int = 3) -> list[str]:
    """
    Remove exact duplicate lines that appear many times (typical headers/footers).
    Keeps lines that look like content (emails/phones).
    """
    normalized = [ln.strip() for ln in lines if ln.strip()]
    counts = Counter(normalized)
    bad = {
        ln
        for ln, c in counts.items()
        if c >= min_count and len(ln) >= min_len and "@" not in ln and not re.search(r"\d", ln)
    }
    if not bad:
        return lines
    return [ln for ln in lines if ln.strip() not in bad]


def preprocess_cv_text(raw: str) -> str:
    text = _normalize_unicode(raw)
    text = _dehyphenate_linebreaks(text)
    text = _normalize_whitespace_keep_newlines(text)

    lines = text.split("\n")
    lines = _drop_obvious_noise_lines(lines)
    lines = _dedupe_repeated_lines(lines)

    out = "\n".join(lines).strip()
    # final: collapse 3+ blank lines
    out = re.sub(r"\n{4,}", "\n\n\n", out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input text file (raw extracted text)")
    ap.add_argument("--out", dest="out", default="", help="Output text file (cleaned)")
    ap.add_argument("--stdout", action="store_true", help="Print cleaned text to stdout")
    args = ap.parse_args()

    with open(args.inp, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    cleaned = preprocess_cv_text(raw)

    if args.stdout or not args.out:
        print(cleaned)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(cleaned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

