"""Quality scoring for document analysis."""

from typing import Dict, List


class QualityScorer:
    """Score document analysis quality."""
    
    def __init__(self):
        self.last_score: float = 0.0
    
    def score_extraction(self, text: str, page_count: int) -> float:
        """Score extraction quality."""
        if not text:
            return 0.0
        
        char_per_page = len(text) / max(1, page_count)
        
        if char_per_page < 100:
            score = 0.3
        elif char_per_page < 500:
            score = 0.6
        else:
            score = 1.0
        
        return round(score, 2)
    
    def score_classification(self, confidence: float) -> float:
        """Score classification quality."""
        return round(min(1.0, confidence), 2)
    
    def score_completeness(self, completeness: float) -> float:
        """Score document completeness."""
        return round(min(1.0, completeness), 2)
    
    def score_overall(self, extraction: float, classification: float, completeness: float) -> float:
        """Calculate overall quality score."""
        weights = {
            "extraction": 0.3,
            "classification": 0.3,
            "completeness": 0.4,
        }
        
        score = (
            extraction * weights["extraction"] +
            classification * weights["classification"] +
            completeness * weights["completeness"]
        )
        
        self.last_score = round(score, 2)
        return self.last_score