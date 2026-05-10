"""Text cleaning utilities."""

import re
from typing import List


class TextCleaner:
    """Clean and normalize extracted text."""
    
    @staticmethod
    def remove_excessive_whitespace(text: str) -> str:
        """Remove excessive whitespace."""
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\n+', '\n\n', text)
        return text.strip()
    
    @staticmethod
    def remove_page_numbers(text: str) -> str:
        """Remove common page number patterns."""
        text = re.sub(r'\n\d+\n', '\n', text)
        text = re.sub(r'Page \d+ (of|/) \d+', '', text, flags=re.IGNORECASE)
        return text
    
    @staticmethod
    def normalize_french_chars(text: str) -> str:
        """Normalize French characters."""
        replacements = {
            'œ': 'oe',
            'æ': 'ae',
            'Œ': 'OE',
            'Æ': 'AE',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def clean(self, text: str) -> str:
        """Apply all cleaning operations."""
        text = self.remove_excessive_whitespace(text)
        text = self.remove_page_numbers(text)
        return text