"""
CV file text extraction utilities.

- PDF: extract digital text with PyMuPDF; OCR pages that look scanned.
- Images: OCR with Tesseract (pytesseract) after light preprocessing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import os
from pathlib import Path

@dataclass
class ExtractedText:
    text: str
    used_ocr: bool
    ocr_pages: list[int]
    page_count: int
    warnings: list[str]


def _lazy_imports():
    # Keep imports local to avoid import-time failures when OCR deps are missing.
    import fitz  # PyMuPDF
    import numpy as np
    import cv2
    import pytesseract

    import shutil

    _configure_tesseract_cmd(pytesseract=pytesseract, shutil=shutil)

    return fitz, np, cv2, pytesseract, shutil


def _configure_tesseract_cmd(*, pytesseract, shutil) -> None:
    """
    Configure pytesseract to find tesseract.exe.

    Priority:
    - env var TESSERACT_CMD (absolute path to tesseract.exe)
    - PATH lookup
    - common Windows install locations
    """
    env_cmd = (os.getenv("TESSERACT_CMD") or "").strip().strip('"')
    if env_cmd and Path(env_cmd).is_file():
        pytesseract.pytesseract.tesseract_cmd = env_cmd
        return

    if shutil.which("tesseract"):
        return

    common = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        str(Path.home() / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe"),
    ]
    for p in common:
        if Path(p).is_file():
            pytesseract.pytesseract.tesseract_cmd = p
            return


def _tesseract_available(*, pytesseract, shutil) -> bool:
    if shutil.which("tesseract"):
        return True
    try:
        _ = pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _determine_skew_angle(gray, *, cv2) -> float:
    """
    Estimate skew angle in degrees using OpenCV.
    Returns a small angle in range about [-45, 45].
    """
    # Binarize: text = 1, background = 0
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bw = 255 - bw

    coords = cv2.findNonZero(bw)
    if coords is None:
        return 0.0

    rect = cv2.minAreaRect(coords)
    angle = float(rect[-1])
    # minAreaRect angle conventions
    if angle < -45:
        angle = 90 + angle
    # Clamp extremely large angles (usually noise)
    if angle > 45:
        angle -= 90
    return angle


def _rotate_image(gray, angle_deg: float, *, cv2):
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=255)


def _preprocess_for_ocr(gray, *, np, cv2):
    # 1) Deskew
    angle = _determine_skew_angle(gray, cv2=cv2)
    if abs(angle) > 0.5:
        gray = _rotate_image(gray, angle, cv2=cv2).astype(np.uint8)

    # 2) Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # 3) CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 4) Otsu binarization
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 5) Upscale x2
    resized = cv2.resize(binary, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized


def ocr_image_bytes(image_bytes: bytes, *, lang: str = "fra+eng") -> str:
    fitz, np, cv2, pytesseract, shutil = _lazy_imports()
    _ = fitz  # silence unused, OCR doesn't need fitz
    if not _tesseract_available(pytesseract=pytesseract, shutil=shutil):
        cmd = getattr(getattr(pytesseract, "pytesseract", None), "tesseract_cmd", "")
        raise RuntimeError(
            "Tesseract not found. Add it to PATH or set env var TESSERACT_CMD "
            f"to the full path of tesseract.exe. Current tesseract_cmd={cmd!r}"
        )

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return ""

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    pre = _preprocess_for_ocr(gray, np=np, cv2=cv2)
    return pytesseract.image_to_string(pre, lang=lang, config="--oem 1 --psm 6").strip()


def extract_text_from_pdf_bytes(
    pdf_bytes: bytes,
    *,
    ocr_if_needed: bool = True,
    force_ocr: bool = False,
    lang: str = "fra+eng",
    min_chars_per_page: int = 40,
    render_dpi: int = 200,
) -> ExtractedText:
    fitz, np, cv2, pytesseract, shutil = _lazy_imports()
    warnings: list[str] = []

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    ocr_pages: list[int] = []
    chunks: list[str] = []

    for i in range(doc.page_count):
        page = doc.load_page(i)
        page_text = ""
        if not force_ocr:
            page_text = (page.get_text("text") or "").strip()

        looks_scanned = force_ocr or (len(page_text) < min_chars_per_page)
        if looks_scanned and ocr_if_needed:
            if not _tesseract_available(pytesseract=pytesseract, shutil=shutil):
                warnings.append("OCR requested but Tesseract is not installed / not in PATH.")
                ocr_if_needed = False
                looks_scanned = False
                # fall back to whatever text was extracted (may be empty)
                if page_text:
                    chunks.append(page_text)
                continue
            # Render -> OCR
            mat = fitz.Matrix(render_dpi / 72.0, render_dpi / 72.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_bytes = pix.tobytes("png")
            arr = np.frombuffer(img_bytes, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                pre = _preprocess_for_ocr(gray, np=np, cv2=cv2)
                ocr_text = pytesseract.image_to_string(
                    pre, lang=lang, config="--oem 1 --psm 6"
                ).strip()
                if ocr_text:
                    ocr_pages.append(i + 1)  # 1-indexed for UX
                    chunks.append(ocr_text)
                    continue

        if page_text:
            chunks.append(page_text)

    text = "\n\n".join([c for c in chunks if c]).strip()
    return ExtractedText(
        text=text,
        used_ocr=bool(ocr_pages),
        ocr_pages=ocr_pages,
        page_count=doc.page_count,
        warnings=warnings,
    )


def _detect_file_kind(file_bytes: bytes, filename: str) -> str:
    """pdf | image | unknown — content sniffing beats filename (Cloudinary URLs often lack extension)."""
    if file_bytes and len(file_bytes) >= 4 and file_bytes[:4] == b"%PDF":
        return "pdf"
    if file_bytes and len(file_bytes) >= 3 and file_bytes[:3] == b"\xff\xd8\xff":
        return "image"
    if (
        file_bytes
        and len(file_bytes) >= 8
        and file_bytes[:8] == b"\x89PNG\r\n\x1a\n"
    ):
        return "image"
    if (
        file_bytes
        and len(file_bytes) >= 12
        and file_bytes[:4] == b"RIFF"
        and file_bytes[8:12] == b"WEBP"
    ):
        return "image"
    if file_bytes and len(file_bytes) >= 2 and file_bytes[:2] in (b"II", b"MM"):
        return "image"

    name = (filename or "").lower()
    if "/image/upload/" in name:
        return "image"
    if name.endswith(".pdf"):
        return "pdf"
    if name.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".bmp", ".gif")):
        return "image"
    return "unknown"


def extract_cv_text_from_file_bytes(
    file_bytes: bytes,
    filename: str,
    *,
    ocr_pdf_if_needed: bool = True,
    force_pdf_ocr: bool = False,
    lang: str = "fra+eng",
) -> ExtractedText:
    kind = _detect_file_kind(file_bytes, filename)

    if kind == "image":
        text = ocr_image_bytes(file_bytes, lang=lang)
        return ExtractedText(text=text, used_ocr=True, ocr_pages=[], page_count=1, warnings=[])

    if kind == "pdf":
        return extract_text_from_pdf_bytes(
            file_bytes,
            ocr_if_needed=ocr_pdf_if_needed,
            force_ocr=force_pdf_ocr,
            lang=lang,
        )

    # Unknown: prefer OCR (mislabeled Cloudinary JPEG sent as .pdf)
    ocr_text = ocr_image_bytes(file_bytes, lang=lang)
    if ocr_text.strip():
        return ExtractedText(text=ocr_text, used_ocr=True, ocr_pages=[], page_count=1, warnings=[])

    try:
        return extract_text_from_pdf_bytes(
            file_bytes,
            ocr_if_needed=ocr_pdf_if_needed,
            force_ocr=force_pdf_ocr,
            lang=lang,
        )
    except Exception:
        return ExtractedText(text="", used_ocr=False, ocr_pages=[], page_count=0, warnings=["Could not parse file as image or PDF."])

