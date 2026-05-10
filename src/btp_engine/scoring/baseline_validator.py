"""Baseline validation for BTP Engine."""

from typing import Dict, List, Optional


class BaselineValidator:
    """Validate results against baseline expectations."""
    
    BASELINE_THRESHOLDS = {
        "extraction_quality": 0.6,
        "classification_confidence": 0.5,
        "completeness": 0.7,
        "overall_quality": 0.65,
    }
    
    def __init__(self):
        self.validation_results: Dict = {}
    
    def validate(self, scores: Dict) -> Dict:
        """Validate scores against baseline."""
        self.validation_results = {
            "passed": True,
            "failures": [],
            "warnings": [],
        }
        
        for metric, threshold in self.BASELINE_THRESHOLDS.items():
            score = scores.get(metric, 0.0)
            
            if score < threshold:
                self.validation_results["passed"] = False
                self.validation_results["failures"].append({
                    "metric": metric,
                    "score": score,
                    "threshold": threshold,
                    "message": f"{metric} below baseline: {score} < {threshold}",
                })
            elif score < threshold + 0.1:
                self.validation_results["warnings"].append({
                    "metric": metric,
                    "score": score,
                    "threshold": threshold,
                    "message": f"{metric} marginally above baseline",
                })
        
        return self.validation_results
    
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.validation_results.get("passed", False)
    
    def get_failures(self) -> List[Dict]:
        """Get validation failures."""
        return self.validation_results.get("failures", [])