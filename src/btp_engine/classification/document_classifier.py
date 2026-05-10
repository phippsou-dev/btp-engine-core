"""Document classifier using pattern matching."""

import re
from typing import Dict, List, Optional
from .class_patterns import ClassificationPatterns
from .class_priority import ClassificationPriority


class DocumentClassifier:
    """Classify BTP documents by type."""
    
    def __init__(self):
        self.patterns = ClassificationPatterns()
        self.last_scores: Dict[str, int] = {}
    
    def classify(self, text: str) -> str:
        """Classify document and return type."""
        text_lower = text.lower()
        scores = {}
        
        for doc_type in self.patterns.all_types():
            score = 0
            for pattern in self.patterns.get_patterns(doc_type):
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            scores[doc_type] = score
        
        self.last_scores = scores
        
        if not scores or max(scores.values()) == 0:
            return "unknown"
        
        return max(scores, key=scores.get)
    
    def classify_with_confidence(self, text: str) -> Dict:
        """Classify with confidence score."""
        doc_type = self.classify(text)
        total_matches = sum(self.last_scores.values())
        
        if total_matches == 0:
            confidence = 0.0
        else:
            confidence = self.last_scores.get(doc_type, 0) / total_matches
        
        priority = ClassificationPriority.from_doc_type(doc_type)
        
        return {
            "type": doc_type,
            "confidence": round(confidence, 2),
            "priority": priority,
            "scores": self.last_scores,
        }