"""OCR using local Tesseract (no Vision API)."""

import os
import subprocess
from typing import Dict, Optional

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def run_ocr_tesseract(filepath: str, lang: str = "fra") -> Dict:
    """
    Run OCR on PDF using local Tesseract.
    
    Args:
        filepath: Path to PDF file
        lang: Tesseract language code (default: fra for French)
        
    Returns:
        dict with keys: filename, text, chars, extraction_ok, error
    """
    result = {
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "text": "",
        "chars": 0,
        "extraction_ok": False,
        "error": None,
        "method": "tesseract_ocr"
    }
    
    if not os.path.exists(filepath):
        result["error"] = f"File not found: {filepath}"
        return result
    
    if not TESSERACT_AVAILABLE:
        result["error"] = "Tesseract/pytesseract not available"
        return result
    
    try:
        # For now, simplified: would need pdftoppm to convert PDF to images first
        # This is a placeholder - real implementation would:
        # 1. Convert PDF pages to images with pdftoppm
        # 2. Run Tesseract on each image
        # 3. Combine results
        
        result["error"] = "OCR pipeline requires pdftoppm + tesseract (not implemented in this version)"
        result["extraction_ok"] = False
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def check_tesseract_available() -> bool:
    """Check if Tesseract is available on system."""
    if not TESSERACT_AVAILABLE:
        return False
    
    try:
        subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
