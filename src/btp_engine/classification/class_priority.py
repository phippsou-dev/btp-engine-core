"""Priority levels for document classification."""

from enum import IntEnum


class ClassificationPriority(IntEnum):
    """Priority levels for document processing."""
    
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    
    @classmethod
    def from_doc_type(cls, doc_type: str) -> int:
        """Get priority from document type."""
        priority_map = {
            "permis": cls.CRITICAL,
            "contrat": cls.CRITICAL,
            "facture": cls.HIGH,
            "rapport": cls.HIGH,
            "devis": cls.MEDIUM,
            "plan": cls.MEDIUM,
        }
        return priority_map.get(doc_type, cls.LOW)