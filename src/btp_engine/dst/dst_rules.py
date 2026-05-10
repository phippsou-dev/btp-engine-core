"""DST rules for document structure mapping."""

from typing import Dict, List


class DSTRules:
    """Define DST rules for different document types."""
    
    STRUCTURE_RULES: Dict[str, Dict] = {
        "facture": {
            "required_sections": ["header", "items", "totals", "footer"],
            "optional_sections": ["notes", "payment_terms"],
            "header_fields": ["numero", "date", "fournisseur", "client"],
            "items_fields": ["designation", "quantite", "prix_unitaire", "total"],
            "totals_fields": ["total_ht", "tva", "total_ttc"],
        },
        "devis": {
            "required_sections": ["header", "items", "totals", "conditions"],
            "optional_sections": ["notes", "validity"],
            "header_fields": ["numero", "date", "validite"],
            "items_fields": ["designation", "quantite", "prix_unitaire"],
        },
        "permis": {
            "required_sections": ["header", "demandeur", "terrain", "projet", "decision"],
            "optional_sections": ["conditions", "recours"],
            "header_fields": ["numero", "date_depot", "reference"],
        },
    }
    
    @classmethod
    def get_structure(cls, doc_type: str) -> Dict:
        """Get structure rules for document type."""
        return cls.STRUCTURE_RULES.get(doc_type, {})
    
    @classmethod
    def get_required_sections(cls, doc_type: str) -> List[str]:
        """Get required sections for document type."""
        structure = cls.get_structure(doc_type)
        return structure.get("required_sections", [])