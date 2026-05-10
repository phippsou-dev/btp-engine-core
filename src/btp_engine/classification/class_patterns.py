"""Classification patterns for BTP documents."""

from typing import Dict, List


class ClassificationPatterns:
    """Define patterns for document classification."""
    
    PATTERNS: Dict[str, List[str]] = {
        "facture": [
            r"facture\s+n[°o]",
            r"invoice\s+number",
            r"montant\s+ht",
            r"montant\s+ttc",
            r"tva",
        ],
        "devis": [
            r"devis\s+n[°o]",
            r"estimation",
            r"quote",
            r"prix\s+unitaire",
            r"total\s+estimatif",
        ],
        "plan": [
            r"plan\s+de",
            r"échelle\s+1:",
            r"architectural\s+plan",
            r"blueprint",
            r"coupe\s+[a-z]-[a-z]",
        ],
        "permis": [
            r"permis\s+de\s+construire",
            r"building\s+permit",
            r"autorisation\s+d'urbanisme",
            r"déclaration\s+préalable",
            r"pc\s+\d{3,}",
        ],
        "rapport": [
            r"rapport\s+technique",
            r"technical\s+report",
            r"compte\s+rendu",
            r"diagnostic",
            r"expertise",
        ],
        "contrat": [
            r"contrat\s+de",
            r"contract",
            r"conditions\s+générales",
            r"signataires",
            r"stipulations",
        ],
    }
    
    @classmethod
    def get_patterns(cls, doc_type: str) -> List[str]:
        """Get patterns for a document type."""
        return cls.PATTERNS.get(doc_type, [])
    
    @classmethod
    def all_types(cls) -> List[str]:
        """Get all document types."""
        return list(cls.PATTERNS.keys())