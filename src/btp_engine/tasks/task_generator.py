"""Task candidate generation."""

from typing import List, Dict
import uuid


def generate_tasks(
    problems: List[Dict],
    expert_flags: set,
    documents: List[Dict]
) -> List[Dict]:
    """
    Generate task candidates from problems, flags, and documents.
    
    Args:
        problems: List of detected problems
        expert_flags: Set of expert flags
        documents: List of classified documents
        
    Returns:
        List of task candidates
    """
    tasks = []
    
    # Tasks from problems
    for problem in problems:
        task = {
            "candidate_id": str(uuid.uuid4()),
            "title": _problem_to_title(problem),
            "description": _problem_to_description(problem),
            "source_files": [problem.get("doc_class", "UNKNOWN")],
            "document_types": [problem.get("doc_class", "UNKNOWN")],
            "evidence": [problem.get("snippet", "")],
            "expert_flags": _problem_to_flags(problem),
            "dst_mapping": _problem_to_dst(problem),
            "confidence": _problem_confidence(problem),
            "human_review_required": problem.get("severity") in ["critical", "high"],
            "category": problem.get("category", "general"),
            "severity": problem.get("severity", "low")
        }
        tasks.append(task)
    
    # Tasks from expert flags
    for flag in expert_flags:
        if flag.startswith("needs_"):
            task = {
                "candidate_id": str(uuid.uuid4()),
                "title": _flag_to_title(flag),
                "description": _flag_to_description(flag),
                "source_files": [],
                "document_types": [],
                "evidence": [],
                "expert_flags": [flag],
                "dst_mapping": _flag_to_dst(flag),
                "confidence": 0.8,
                "human_review_required": True,
                "category": "expert_required",
                "severity": "medium"
            }
            tasks.append(task)
    
    return tasks


def _problem_to_title(problem: Dict) -> str:
    """Convert problem to task title."""
    category = problem.get("category", "general")
    titles = {
        "structural": "Traiter problème structurel",
        "humidity": "Traiter problème d'humidité",
        "electrical": "Mise en conformité électrique",
        "insalubrity": "Lever insalubrité",
        "hazmat": "Traiter matériaux dangereux",
        "safety": "Mise en sécurité"
    }
    return titles.get(category, "Problème détecté")


def _problem_to_description(problem: Dict) -> str:
    """Convert problem to task description."""
    return f"Problème détecté : {problem.get('keyword', 'non spécifié')}"


def _problem_to_flags(problem: Dict) -> List[str]:
    """Convert problem to expert flags."""
    category = problem.get("category")
    flag_map = {
        "hazmat": ["needs_diagnostic", "regulatory_required"],
        "insalubrity": ["needs_insalubrite", "regulatory_required"],
        "electrical": ["needs_electricien_qualifie"],
        "structural": ["needs_BET"]
    }
    return flag_map.get(category, [])


def _problem_to_dst(problem: Dict) -> List[str]:
    """Map problem to DST families."""
    category = problem.get("category")
    dst_map = {
        "structural": ["FT06_structure_gros_oeuvre"],
        "humidity": ["FT10_etancheite"],
        "electrical": ["FT26_electricite_CFO"],
        "insalubrity": ["FT02_etudes_diagnostics", "FT03_curage_depose"],
        "hazmat": ["FT02_etudes_diagnostics", "FT03_curage_depose"]
    }
    return dst_map.get(category, [])


def _problem_confidence(problem: Dict) -> float:
    """Get confidence score for problem-based task."""
    severity = problem.get("severity", "low")
    confidence_map = {
        "critical": 0.95,
        "high": 0.85,
        "medium": 0.70,
        "low": 0.60
    }
    return confidence_map.get(severity, 0.60)


def _flag_to_title(flag: str) -> str:
    """Convert expert flag to task title."""
    titles = {
        "needs_ABF": "Obtenir validation ABF",
        "needs_BET": "Faire intervenir BET",
        "needs_diagnostic": "Réaliser diagnostic complémentaire",
        "needs_plomb": "Traiter plomb (CREP)",
        "needs_amiante": "Traiter amiante (DTA)",
        "needs_electricien_qualifie": "Mise en conformité électrique",
        "needs_securite_incendie": "Installer système sécurité incendie",
        "needs_insalubrite": "Lever arrêté insalubrité",
        "needs_ERP_review": "Revue ERP",
        "needs_assainissement_review": "Mise en conformité assainissement",
        "needs_termites_review": "Traiter termites"
    }
    return titles.get(flag, flag)


def _flag_to_description(flag: str) -> str:
    """Convert expert flag to task description."""
    descriptions = {
        "needs_ABF": "Validation Architecte des Bâtiments de France obligatoire",
        "needs_BET": "Intervention Bureau d'Études Techniques requise",
        "needs_diagnostic": "Diagnostic complémentaire à réaliser",
        "needs_plomb": "Traitement plomb selon CREP",
        "needs_amiante": "Traitement amiante selon DTA",
        "needs_electricien_qualifie": "Mise en conformité par électricien qualifié",
        "needs_securite_incendie": "Installation SSI selon notice sécurité",
        "needs_insalubrite": "Travaux pour lever arrêté insalubrité",
        "needs_ERP_review": "Analyse État des Risques et Pollutions",
        "needs_assainissement_review": "Conformité assainissement à vérifier",
        "needs_termites_review": "Traitement termites si présence confirmée"
    }
    return descriptions.get(flag, flag)


def _flag_to_dst(flag: str) -> List[str]:
    """Map expert flag to DST families."""
    dst_map = {
        "needs_ABF": ["FT01_pilotage_autorisations"],
        "needs_BET": ["FT02_etudes_diagnostics"],
        "needs_diagnostic": ["FT02_etudes_diagnostics"],
        "needs_plomb": ["FT03_curage_depose"],
        "needs_amiante": ["FT03_curage_depose"],
        "needs_electricien_qualifie": ["FT26_electricite_CFO"],
        "needs_securite_incendie": ["FT27_courants_faibles_SSI"],
        "needs_insalubrite": ["FT02_etudes_diagnostics", "FT03_curage_depose"],
        "needs_ERP_review": ["FT01_pilotage_autorisations"],
        "needs_assainissement_review": ["FT23_plomberie"],
        "needs_termites_review": ["FT03_curage_depose"]
    }
    return dst_map.get(flag, [])
