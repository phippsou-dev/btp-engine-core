"""Baseline validation for BTP Engine - Strict Gambetta-style validation."""

from typing import Dict, List, Optional
from enum import Enum


class BaselineStatus(str, Enum):
    """Baseline validation status."""
    PASS = "PASS"
    FAIL = "FAIL"
    WEAK = "WEAK"
    INCOMPATIBLE_SOURCE = "INCOMPATIBLE_SOURCE"


FORBIDDEN_SOURCE_RULES = {
    "CF": ["DPE", "DPE_AUTRES_BATIMENTS", "DIAGNOSTIC_PLOMB_CREP", "DIAGNOSTIC_TERMITES"],
    "structure": ["DPE", "DPE_AUTRES_BATIMENTS", "DIAGNOSTIC_PLOMB_CREP", "DIAGNOSTIC_TERMITES"],
    "facade": ["DPE", "DPE_AUTRES_BATIMENTS", "DIAGNOSTIC_PLOMB_CREP", "DIAGNOSTIC_TERMITES"],
    "EP": ["DPE", "DPE_AUTRES_BATIMENTS", "DIAGNOSTIC_PLOMB_CREP", "DIAGNOSTIC_TERMITES"],
    "eaux_pluviales": ["DPE", "DPE_AUTRES_BATIMENTS", "DIAGNOSTIC_PLOMB_CREP", "DIAGNOSTIC_TERMITES"],
    "plans": ["DPE", "DPE_AUTRES_BATIMENTS", "DIAGNOSTIC_PLOMB_CREP", "DIAGNOSTIC_TERMITES"],
    "menuiseries": ["DIAGNOSTIC_TERMITES"],
}


class BaselineValidator:
    """Validate results against baseline expectations with strict rules."""
    
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
    
    def validate_task_baseline(self, candidate: dict, baseline_item: dict) -> dict:
        """Validate a task candidate against baseline item.
        
        Args:
            candidate: Task candidate with source_file, evidence, etc.
            baseline_item: Baseline item with required_triggers, allowed_classes, etc.
            
        Returns:
            Validation result with status, reasons, etc.
        """
        result = {
            "status": BaselineStatus.FAIL,
            "reasons": [],
            "candidate": candidate,
            "baseline_item": baseline_item,
        }
        
        # Rule 1: No PASS without source
        source_file = candidate.get("source_file") or candidate.get("source_files")
        if not source_file:
            result["reasons"].append("Missing source_file or source_files")
            result["status"] = BaselineStatus.FAIL
            return result
        
        # Rule 2: No PASS without evidence
        evidence = candidate.get("evidence") or candidate.get("evidence_excerpt")
        if not evidence or (isinstance(evidence, str) and not evidence.strip()):
            result["reasons"].append("Missing or empty evidence")
            result["status"] = BaselineStatus.FAIL
            return result
        
        # Rule 4: Check source class compatibility
        source_class = candidate.get("source_class")
        allowed_classes = baseline_item.get("allowed_classes", [])
        
        if allowed_classes and source_class not in allowed_classes:
            result["reasons"].append(f"Source class '{source_class}' not in allowed classes")
            result["status"] = BaselineStatus.INCOMPATIBLE_SOURCE
            return result
        
        # Rule 5: Check required triggers
        required_triggers = baseline_item.get("required_triggers", [])
        evidence_str = str(evidence).lower()
        
        missing_triggers = []
        for trigger in required_triggers:
            if trigger.lower() not in evidence_str:
                missing_triggers.append(trigger)
        
        if missing_triggers:
            result["reasons"].append(f"Missing required triggers: {missing_triggers}")
            result["status"] = BaselineStatus.FAIL
            return result
        
        # Rules 6-9: Check forbidden source classes
        baseline_domain = baseline_item.get("domain") or baseline_item.get("task_type")
        if baseline_domain and source_class:
            forbidden_sources = FORBIDDEN_SOURCE_RULES.get(baseline_domain, [])
            if source_class in forbidden_sources:
                result["reasons"].append(
                    f"Forbidden source: {source_class} cannot prove {baseline_domain}"
                )
                result["status"] = BaselineStatus.INCOMPATIBLE_SOURCE
                return result
        
        # If all checks pass
        result["status"] = BaselineStatus.PASS
        result["reasons"].append("All strict validation checks passed")
        return result
    
    def validate_document_presence(self, document: dict, baseline_item: dict) -> dict:
        """Validate document presence against baseline.
        
        Args:
            document: Document with filename, sha256, class, etc.
            baseline_item: Baseline item for document presence
            
        Returns:
            Validation result
        """
        result = {
            "status": BaselineStatus.FAIL,
            "reasons": [],
            "document": document,
            "baseline_item": baseline_item,
        }
        
        # Rule 3: DOCUMENT_PRESENCE can PASS with filename + sha256 + class
        filename = document.get("filename")
        sha256 = document.get("sha256")
        doc_class = document.get("class") or document.get("document_class")
        
        if not filename:
            result["reasons"].append("Missing filename")
            return result
        
        if not sha256:
            result["reasons"].append("Missing sha256")
            return result
        
        if not doc_class:
            result["reasons"].append("Missing document class")
            return result
        
        # Check allowed classes
        allowed_classes = baseline_item.get("allowed_classes", [])
        if allowed_classes and doc_class not in allowed_classes:
            result["reasons"].append(f"Document class '{doc_class}' not in allowed classes")
            result["status"] = BaselineStatus.INCOMPATIBLE_SOURCE
            return result
        
        result["status"] = BaselineStatus.PASS
        result["reasons"].append("Document presence validated")
        return result
    
    def validate_all(self, candidates: list, documents: list, baseline_items: list) -> dict:
        """Validate all candidates and documents against baseline items.
        
        Args:
            candidates: List of task candidates
            documents: List of documents
            baseline_items: List of baseline items
            
        Returns:
            Aggregate validation results with counters
        """
        results = {
            "baseline_total_count": len(baseline_items),
            "baseline_pass_strict_count": 0,
            "baseline_fail_strict_count": 0,
            "baseline_weak_count": 0,
            "baseline_evidence_invalid_count": 0,
            "empty_evidence_pass_count": 0,
            "wrong_source_class_pass_count": 0,
            "missing_trigger_count": 0,
            "forbidden_source_pass_count": 0,
            "validations": [],
        }
        
        for baseline_item in baseline_items:
            baseline_type = baseline_item.get("type")
            
            if baseline_type == "TASK_BASELINE":
                # Find matching candidate
                matched = False
                for candidate in candidates:
                    validation = self.validate_task_baseline(candidate, baseline_item)
                    results["validations"].append(validation)
                    
                    if validation["status"] == BaselineStatus.PASS:
                        results["baseline_pass_strict_count"] += 1
                        matched = True
                        
                        # Check for invalid PASS (should never happen)
                        evidence = candidate.get("evidence") or candidate.get("evidence_excerpt")
                        if not evidence or not str(evidence).strip():
                            results["empty_evidence_pass_count"] += 1
                        
                        break
                    elif validation["status"] == BaselineStatus.INCOMPATIBLE_SOURCE:
                        results["wrong_source_class_pass_count"] += 1
                    elif "Missing required triggers" in str(validation.get("reasons")):
                        results["missing_trigger_count"] += 1
                    elif "Forbidden source" in str(validation.get("reasons")):
                        results["forbidden_source_pass_count"] += 1
                
                if not matched:
                    results["baseline_fail_strict_count"] += 1
            
            elif baseline_type == "DOCUMENT_PRESENCE_BASELINE":
                matched = False
                for document in documents:
                    validation = self.validate_document_presence(document, baseline_item)
                    results["validations"].append(validation)
                    
                    if validation["status"] == BaselineStatus.PASS:
                        results["baseline_pass_strict_count"] += 1
                        matched = True
                        break
                
                if not matched:
                    results["baseline_fail_strict_count"] += 1
        
        return results