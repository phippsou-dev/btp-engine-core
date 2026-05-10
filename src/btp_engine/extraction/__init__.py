"""Extraction module - Document content extraction.

Exposes both class API (PDFExtractor, OCREngine, TextCleaner) and the
functional API used by scripts/run_engine.py:

    extract_pdf_text(filepath) -> dict with text, page_count, native_chars,
                                  ocr_executed, ocr_chars, filename, sha256.

OCR fallback policy (LOCAL ONLY — no Vision API):
- triggered if native_chars < 100
- triggered if cid_ratio > 0.5 (text dominated by (cid:NN) glyphs)
- uses pdftoppm @ 250 DPI + tesseract fra --psm 6
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

from .pdf_to_text import PDFExtractor
from .ocr_tesseract import OCREngine
from .text_cleaner import TextCleaner

__all__ = [
    "PDFExtractor",
    "OCREngine",
    "TextCleaner",
    "extract_pdf_text",
    "ocr_pdf_local",
    "needs_ocr_fallback",
]


_CID_RE = re.compile(r"\(cid:\d+\)")


def needs_ocr_fallback(text: str, min_native_chars: int = 100) -> bool:
    """Return True if local OCR fallback should be triggered."""
    if not text or len(text.strip()) < min_native_chars:
        return True
    cid_count = len(_CID_RE.findall(text))
    # ratio of CID glyphs to total non-space tokens ish
    tokens = max(1, len(text) // 6)
    if cid_count / tokens > 0.5:
        return True
    return False


def _sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ocr_pdf_local(filepath: str, lang: str = "fra", dpi: int = 200) -> str:
    """Run local OCR (pdftoppm + tesseract). No external API."""
    if not shutil.which("pdftoppm"):
        return ""
    if not shutil.which("tesseract"):
        return ""
    out_chunks = []
    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = os.path.join(tmpdir, "page")
        try:
            subprocess.run(
                ["pdftoppm", "-r", str(dpi), "-png", filepath, prefix],
                check=True,
                capture_output=True,
                timeout=300,
            )
        except Exception:
            return ""
        images = sorted(Path(tmpdir).glob("page-*.png"))
        for img in images:
            try:
                proc = subprocess.run(
                    ["tesseract", str(img), "-", "-l", lang, "--psm", "6"],
                    check=True,
                    capture_output=True,
                    timeout=120,
                )
                out_chunks.append(proc.stdout.decode("utf-8", errors="replace"))
            except Exception:
                continue
    return "\n\n".join(out_chunks)


def extract_pdf_text(filepath: str) -> Dict:
    """Functional wrapper: extract text + metadata + OCR fallback if needed."""
    extractor = PDFExtractor()
    meta = extractor.extract_with_metadata(filepath)
    native_text = meta.get("text", "") or ""
    native_chars = len(native_text)
    page_count = meta.get("page_count", 0)

    # Detect CID-dominated text (notice_securite case)
    cid_count = len(_CID_RE.findall(native_text))
    tokens = max(1, native_chars // 6)
    cid_dominated = (cid_count / tokens) > 0.5

    ocr_executed = False
    ocr_chars = 0
    final_text = native_text
    if needs_ocr_fallback(native_text):
        ocr_text = ocr_pdf_local(filepath)
        if ocr_text and len(ocr_text.strip()) >= 100:
            ocr_executed = True
            ocr_chars = len(ocr_text)
            if cid_dominated or native_chars < 100:
                # Replace garbled native text with OCR
                final_text = ocr_text
            else:
                final_text = ocr_text + "\n\n" + native_text

    return {
        "filename": Path(filepath).name,
        "filepath": str(filepath),
        "sha256": _sha256_file(filepath),
        "text": final_text,
        "page_count": page_count,
        "native_chars": native_chars,
        "ocr_executed": ocr_executed,
        "ocr_chars": ocr_chars,
        "cid_count": cid_count,
        "char_count": len(final_text),
    }
