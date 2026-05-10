"""Expert rules for document analysis."""

from typing import Dict, List


class ExpertRules:
    """Define expert rules for document analysis."""
    
    PROBLEM_RULES: Dict[str, List[Dict]] = {
        "facture": [
            {
                "pattern": r"montant\s+ttc\s*:\s*0",
                "severity": "critical",
                "description": "Montant TTC nul",
            },
            {
                "pattern": r"tva\s+non\s+applicable",
                "severity": "medium",
                "description": "TVA non applicable",
            },
        ],
        "devis": [
            {
                "pattern": r"prix\s+à\s+définir",
                "severity": "high",
                "description": "Prix à définir",
            },
            {
                "pattern": r"sous\s+réserve",
                "severity": "medium",
                "description": "Clause de réserve",
            },
        ],
        "permis": [
            {
                "pattern": r"refusé|rejeté|rejected",
                "severity": "critical",
                "description": "Permis refusé",
            },
            {
                "pattern": r"incomplet|incomplete",
                "severity": "high",
                "description": "Dossier incomplet",
            },
        ],
    }
    
    def get_problem_patterns(self, doc_type: str) -> List[Dict]:
        """Get problem patterns for document type."""
        return self.PROBLEM_RULES.get(doc_type, [])
    
    def all_doc_types(self) -> List[str]:
        """Get all document types with rules."""
        return list(self.PROBLEM_RULES.keys())