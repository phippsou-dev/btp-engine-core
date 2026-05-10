"""OCR using Tesseract."""

from pathlib import Path
from typing import Optional
import pytesseract
from PIL import Image


class OCREngine:
    """Perform OCR on images using Tesseract."""
    
    def __init__(self, lang: str = "fra+eng"):
        self.lang = lang
    
    def extract(self, filepath: str) -> str:
        """Extract text from image file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {filepath}")
        
        try:
            image = Image.open(filepath)
            text = pytesseract.image_to_string(image, lang=self.lang)
            return text
        except Exception as e:
            raise RuntimeError(f"OCR failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Tesseract is available."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False