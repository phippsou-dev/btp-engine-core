"""Flag detector for document analysis."""

import re
from typing import Dict, List


class FlagDetector:
    """Detect flags and warnings in documents."""
    
    FLAG_PATTERNS = {
        "missing_signature": {
            "pattern": r"signature\s+manquante|non\s+signé|unsigned",
            "severity": "high",
        },
        "incomplete_data": {
            "pattern": r"incomplet|données\s+manquantes|missing\s+data",
            "severity": "medium",
        },
        "expired": {
            "pattern": r"expiré|périmé|expired",
            "severity": "high",
        },
        "non_compliant": {
            "pattern": r"non\s+conforme|not\s+compliant|violation",
            "severity": "critical",
        },
    }
    
    def __init__(self):
        self.detected_flags: List[Dict] = []
    
    def detect(self, text: str) -> List[Dict]:
        """Detect flags in text."""
        self.detected_flags.clear()
        text_lower = text.lower()
        
        for flag_name, info in self.FLAG_PATTERNS.items():
            matches = re.finditer(info["pattern"], text_lower, re.IGNORECASE)
            for match in matches:
                self.detected_flags.append({
                    "flag": flag_name,
                    "severity": info["severity"],
                    "matched_text": match.group(0),
                    "position": match.start(),
                })
        
        return self.detected_flags
    
    def get_critical_flags(self) -> List[Dict]:
        """Get only critical flags."""
        return [f for f in self.detected_flags if f["severity"] == "critical"]