"""Map document content to DST structure."""

from typing import Dict, List, Optional
from .dst_rules import DSTRules


class DSTMapper:
    """Map document to Document Structure Tree."""
    
    def __init__(self):
        self.rules = DSTRules()
        self.mapped_structure: Dict = {}
    
    def map_document(self, text: str, doc_type: str) -> Dict:
        """Map document text to DST structure."""
        structure = self.rules.get_structure(doc_type)
        required_sections = structure.get("required_sections", [])
        
        self.mapped_structure = {
            "doc_type": doc_type,
            "sections": {},
            "completeness": 0.0,
        }
        
        text_lower = text.lower()
        found_sections = []
        
        for section in required_sections:
            if section in text_lower:
                found_sections.append(section)
                self.mapped_structure["sections"][section] = {
                    "found": True,
                    "content_preview": self._extract_section_preview(text, section),
                }
            else:
                self.mapped_structure["sections"][section] = {
                    "found": False,
                    "content_preview": None,
                }
        
        if required_sections:
            completeness = len(found_sections) / len(required_sections)
            self.mapped_structure["completeness"] = round(completeness, 2)
        
        return self.mapped_structure
    
    def _extract_section_preview(self, text: str, section: str, max_len: int = 100) -> str:
        """Extract preview of section content."""
        text_lower = text.lower()
        idx = text_lower.find(section)
        if idx == -1:
            return ""
        
        preview = text[idx:idx + max_len]
        return preview.strip()
    
    def get_missing_sections(self) -> List[str]:
        """Get list of missing required sections."""
        missing = []
        for section, info in self.mapped_structure.get("sections", {}).items():
            if not info.get("found"):
                missing.append(section)
        return missing