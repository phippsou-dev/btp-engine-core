"""Task templates for common BTP scenarios."""

TASK_TEMPLATES = {
    "electrical_compliance": {
        "title": "Mise en conformité électrique",
        "description": "Mise aux normes de l'installation électrique",
        "dst_family": "FT26_electricite_CFO",
        "typical_duration_days": 5,
        "typical_cost_range": "2000-8000",
        "requires_certification": True
    },
    
    "lead_treatment": {
        "title": "Traitement plomb",
        "description": "Traitement des peintures au plomb selon CREP",
        "dst_family": "FT03_curage_depose",
        "typical_duration_days": 10,
        "typical_cost_range": "5000-15000",
        "requires_certification": True
    },
    
    "asbestos_removal": {
        "title": "Désamiantage",
        "description": "Retrait amiante par entreprise certifiée",
        "dst_family": "FT03_curage_depose",
        "typical_duration_days": 15,
        "typical_cost_range": "10000-50000",
        "requires_certification": True
    },
    
    "humidity_treatment": {
        "title": "Traitement humidité",
        "description": "Traitement infiltrations et humidité",
        "dst_family": "FT10_etancheite",
        "typical_duration_days": 7,
        "typical_cost_range": "3000-12000",
        "requires_certification": False
    },
    
    "structural_repair": {
        "title": "Réparation structure",
        "description": "Réparation/renforcement structure",
        "dst_family": "FT06_structure_gros_oeuvre",
        "typical_duration_days": 20,
        "typical_cost_range": "15000-100000",
        "requires_certification": False
    },
}


def get_task_template(template_name: str) -> dict:
    """Get task template by name."""
    return TASK_TEMPLATES.get(template_name, {})


def list_templates() -> list:
    """List all available templates."""
    return list(TASK_TEMPLATES.keys())
