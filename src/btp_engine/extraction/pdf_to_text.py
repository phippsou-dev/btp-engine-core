"""PDF text extraction using pdfplumber."""

from pathlib import Path
from typing import Dict, List, Optional
import pdfplumber


class PDFExtractor:
    """Extract text from PDF documents."""
    
    def __init__(self):
        self.last_page_count = 0
    
    def extract(self, filepath: str) -> str:
        """Extract text from PDF file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {filepath}")
        
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF file: {filepath}")
        
        texts = []
        try:
            with pdfplumber.open(filepath) as pdf:
                self.last_page_count = len(pdf.pages)
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        texts.append(text)
        except Exception as e:
            raise RuntimeError(f"PDF extraction failed: {e}")
        
        return "\n\n".join(texts)
    
    def extract_with_metadata(self, filepath: str) -> Dict:
        """Extract text with metadata."""
        text = self.extract(filepath)
        return {
            "text": text,
            "page_count": self.last_page_count,
            "char_count": len(text),
            "filepath": str(filepath),
        }
