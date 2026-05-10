"""Detect problems in BTP documents."""

import re
from typing import Dict, List
from .expert_rules import ExpertRules


class ProblemDetector:
    """Detect problems and anomalies in documents."""
    
    def __init__(self):
        self.rules = ExpertRules()
        self.detected_problems: List[Dict] = []
    
    def detect(self, text: str, doc_type: str) -> List[Dict]:
        """Detect problems in document text."""
        self.detected_problems.clear()
        text_lower = text.lower()
        
        problem_patterns = self.rules.get_problem_patterns(doc_type)
        
        for pattern_info in problem_patterns:
            pattern = pattern_info["pattern"]
            severity = pattern_info["severity"]
            description = pattern_info["description"]
            
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                self.detected_problems.append({
                    "type": "problem",
                    "severity": severity,
                    "description": description,
                    "matched_text": match.group(0),
                    "position": match.start(),
                })
        
        return self.detected_problems
    
    def get_critical_problems(self) -> List[Dict]:
        """Get only critical problems."""
        return [p for p in self.detected_problems if p["severity"] == "critical"]
    
    def has_critical_problems(self) -> bool:
        """Check if critical problems exist."""
        return len(self.get_critical_problems()) > 0