"""PDF text extraction using native methods (pdfplumber)."""

import os
from typing import Dict, Optional

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def extract_pdf_text(filepath: str, ocr_chars_min: int = 100) -> Dict:
    """
    Extract text from PDF using native extraction.
    
    Args:
        filepath: Path to PDF file
        ocr_chars_min: Minimum characters to consider extraction successful
        
    Returns:
        dict with keys: filename, text, chars, pages, extraction_ok, needs_ocr
    """
    result = {
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "text": "",
        "chars": 0,
        "pages": 0,
        "extraction_ok": False,
        "needs_ocr": False,
        "error": None,
    }
    
    if not os.path.exists(filepath):
        result["error"] = f"File not found: {filepath}"
        return result
    
    if not PDFPLUMBER_AVAILABLE:
        result["error"] = "pdfplumber not available"
        result["needs_ocr"] = True
        return result
    
    try:
        with pdfplumber.open(filepath) as pdf:
            result["pages"] = len(pdf.pages)
            
            all_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text.append(page_text)
            
            result["text"] = "\n\n".join(all_text)
            result["chars"] = len(result["text"])
            
            # Check if extraction was successful
            if result["chars"] >= ocr_chars_min:
                result["extraction_ok"] = True
                result["needs_ocr"] = False
            else:
                result["extraction_ok"] = False
                result["needs_ocr"] = True
                
    except Exception as e:
        result["error"] = str(e)
        result["needs_ocr"] = True
    
    return result
