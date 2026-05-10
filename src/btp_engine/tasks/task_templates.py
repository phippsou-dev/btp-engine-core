"""Task templates for different document types."""

from typing import Dict, List


class TaskTemplates:
    """Templates for generating tasks."""
    
    TEMPLATES: Dict[str, List[Dict]] = {
        "facture": [
            {
                "name": "Vérifier montants",
                "priority": "high",
                "description": "Vérifier cohérence HT/TTC/TVA",
            },
            {
                "name": "Archiver facture",
                "priority": "medium",
                "description": "Archiver dans système comptable",
            },
        ],
        "devis": [
            {
                "name": "Valider devis",
                "priority": "high",
                "description": "Valider conformité et prix",
            },
            {
                "name": "Négocier tarifs",
                "priority": "medium",
                "description": "Négocier si nécessaire",
            },
        ],
        "permis": [
            {
                "name": "Vérifier validité",
                "priority": "critical",
                "description": "Vérifier dates et conditions",
            },
            {
                "name": "Archiver permis",
                "priority": "high",
                "description": "Archiver dans dossier chantier",
            },
        ],
        "rapport": [
            {
                "name": "Analyser rapport",
                "priority": "high",
                "description": "Analyser conclusions et recommandations",
            },
            {
                "name": "Planifier actions",
                "priority": "medium",
                "description": "Planifier actions correctives",
            },
        ],
    }
    
    @classmethod
    def get_templates(cls, doc_type: str) -> List[Dict]:
        """Get task templates for document type."""
        return cls.TEMPLATES.get(doc_type, [])
    
    @classmethod
    def all_types(cls) -> List[str]:
        """Get all document types with templates."""
        return list(cls.TEMPLATES.keys())