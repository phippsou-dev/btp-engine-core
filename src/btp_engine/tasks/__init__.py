"""Tasks module - deterministic task generation from flags (no GPT)."""

from typing import Dict, Iterable, List, Optional, Set

from .task_generator import TaskGenerator
from .task_templates import TaskTemplates
from .task_merger import TaskMerger

__all__ = [
    "TaskGenerator",
    "TaskTemplates",
    "TaskMerger",
    "generate_tasks",
    "merge_similar_tasks",
    "FLAG_TO_TASK",
]


# Deterministic flag -> task mapping (Phase 6).
# Each entry: (title, ft_codes, priority).
# Advisory DPE flags are intentionally EXCLUDED from tasks.
FLAG_TO_TASK: Dict[str, Dict] = {
    # NOTICE_SECURITE
    "cages_escalier": {"title": "Vérifier conformité cages d'escalier (CF/désenfumage)", "ft": ["FT27", "FT16"], "priority": "high"},
    "desenfumage": {"title": "Vérifier dispositif de désenfumage", "ft": ["FT27"], "priority": "high"},
    "coupe_feu": {"title": "Vérifier degré coupe-feu (CF1h)", "ft": ["FT27", "FT16"], "priority": "high"},
    "batiments_habitation": {"title": "Confirmer typologie bâtiment d'habitation (1ère/2ème famille)", "ft": ["FT27"], "priority": "medium"},
    "permis_construire_coche": {"title": "Vérifier dépôt PC associé à la notice sécurité", "ft": ["FT27"], "priority": "medium"},
    "maitre_oeuvre": {"title": "Confirmer maîtrise d'œuvre (architecte) sur dossier", "ft": ["FT27"], "priority": "medium"},
    "etablissement_identifie": {"title": "Identifier l'établissement objet de la notice", "ft": ["FT27"], "priority": "medium"},
    "demandeur": {"title": "Identifier le demandeur du dossier sécurité", "ft": ["FT27"], "priority": "low"},
    "adresse": {"title": "Vérifier adresse exacte du projet", "ft": ["FT27"], "priority": "low"},
    "commune": {"title": "Vérifier commune et code postal", "ft": ["FT27"], "priority": "low"},

    # DPE (NON advisory)
    "needs_thermique_DPE": {"title": "Intégrer DPE projeté au dossier thermique", "ft": ["FT24"], "priority": "high"},
    "PAC_air_air": {"title": "Installer PAC air/air conformément au DPE projeté", "ft": ["FT24", "FT25"], "priority": "high"},
    "chauffe_eau_thermodynamique": {"title": "Installer chauffe-eau thermodynamique", "ft": ["FT24", "FT25"], "priority": "high"},
    "VMC_Hygro_B": {"title": "Mettre en œuvre VMC SF Hygro B", "ft": ["FT13"], "priority": "high"},
    "isolation_R_3_7": {"title": "Atteindre R≥3,7 m².K/W sur l'isolation", "ft": ["FT02"], "priority": "high"},
    "fenetres_double_vitrage": {"title": "Poser menuiseries double vitrage performantes", "ft": ["FT02"], "priority": "medium"},
    "portes_performantes": {"title": "Poser portes performantes (isolation)", "ft": ["FT02"], "priority": "medium"},
    # exclude_advisory_from_tasks intentionally not mapped

    # EDL
    "local_commercial_non_visite": {"title": "Planifier visite du local commercial non visité", "ft": ["FT02"], "priority": "high"},
    "appartement_R1_non_visite": {"title": "Planifier visite appartement R+1 non visité", "ft": ["FT02"], "priority": "high"},
    "PC_deja_realise": {"title": "Récupérer PC déjà déposé / accord", "ft": ["FT02"], "priority": "medium"},
    "cheminees_plafonds_moulures": {"title": "Conserver/traiter cheminées et plafonds moulurés", "ft": ["FT11", "FT13"], "priority": "medium"},
    "reseaux_fioul_gaz": {"title": "Dépose réseaux fioul/gaz existants", "ft": ["FT23", "FT25", "FT26"], "priority": "high"},
    "plancher_R4_affaisse": {"title": "Renforcer plancher R+4 affaissé (mission BET)", "ft": ["FT06", "FT03"], "priority": "critical"},
    "plancher_connecte": {"title": "Désolidariser plancher connecté", "ft": ["FT06"], "priority": "high"},
    "facade_fissuree": {"title": "Traiter façade fissurée (diagnostic + reprise)", "ft": ["FT11"], "priority": "high"},
    "renfort_sous_toiture": {"title": "Mettre en œuvre renfort sous toiture", "ft": ["FT06", "FT10"], "priority": "high"},
    "evacuations_amiante": {"title": "Évacuation amiante (filière agréée)", "ft": ["FT30"], "priority": "critical"},
    "toiture_fibrociment_amiante": {"title": "Désamiantage toiture fibrociment", "ft": ["FT30", "FT10"], "priority": "critical"},
    "coupe_feu_cage_escalier": {"title": "Mise en conformité coupe-feu cage d'escalier", "ft": ["FT27", "FT16"], "priority": "high"},
    "portes_palieres_CF1h": {"title": "Pose portes palières CF1h", "ft": ["FT27", "FT16"], "priority": "high"},
    "lanterneau_desenfumage": {"title": "Installer lanterneau de désenfumage", "ft": ["FT27", "FT10"], "priority": "high"},
    "needs_diagnostic": {"title": "Lancer diagnostics complémentaires", "ft": ["FT02"], "priority": "high"},
    "needs_BET": {"title": "Mandater BET structure", "ft": ["FT06"], "priority": "high"},
    "needs_securite_incendie": {"title": "Mission sécurité incendie", "ft": ["FT27"], "priority": "high"},
    "needs_ABF": {"title": "Consultation ABF (architecte des bâtiments de France)", "ft": ["FT02"], "priority": "high"},

    # PLAN_GRAPHIC_PC_FACADES
    "PC_22T0205": {"title": "Référencer PC 22T0205 dans le dossier", "ft": ["FT01"], "priority": "medium"},
    "renovation_facades": {"title": "Rénovation façades selon plans PC", "ft": ["FT11"], "priority": "high"},
    "descentes_EP": {"title": "Reprise descentes EP", "ft": ["FT13", "FT14"], "priority": "medium"},
    "enduit_ciment_decroute": {"title": "Décrouter enduit ciment existant", "ft": ["FT11"], "priority": "high"},
    "enduit_chaux_ton_pierre": {"title": "Appliquer enduit 100% chaux ton pierre", "ft": ["FT11"], "priority": "high"},
    "chainages_angles": {"title": "Reprise chaînages d'angles", "ft": ["FT11", "FT10"], "priority": "high"},
    "corniche_genoises": {"title": "Restaurer corniches et génoises", "ft": ["FT11"], "priority": "medium"},
    "menuiseries_bois_R2_R3": {"title": "Conserver/restaurer menuiseries bois R+2/R+3", "ft": ["FT13"], "priority": "medium"},
    "menuiseries_PVC_R1_remplacees": {"title": "Remplacer menuiseries PVC R+1", "ft": ["FT13"], "priority": "medium"},
    "porte_acier_conservee": {"title": "Conserver porte acier", "ft": ["FT13"], "priority": "low"},
    "lambrequins_non_conserves": {"title": "Dépose lambrequins (non conservés)", "ft": ["FT11"], "priority": "low"},
    "garde_corps_traites": {"title": "Traiter garde-corps / ferronneries", "ft": ["FT14"], "priority": "medium"},
    "vitrines_RDC_exclues": {"title": "Acter exclusion vitrines RDC du périmètre", "ft": ["FT11"], "priority": "low"},
}


def _excerpt(text: str, needle: str, span: int = 120) -> str:
    if not text or not needle:
        return ""
    lc = text.lower()
    idx = lc.find(needle.lower())
    if idx < 0:
        return needle
    start = max(0, idx - span // 2)
    end = min(len(text), idx + len(needle) + span // 2)
    return text[start:end].replace("\n", " ").strip()


def generate_tasks(problems: List[Dict], flags: Iterable, documents: List[Dict]) -> List[Dict]:
    """Deterministic generator. flags can be a set of strings or list of dicts."""
    tasks: List[Dict] = []
    if not documents:
        return tasks

    # Normalize flags to per-doc structure: walk docs to attach evidence
    flag_set: Set[str] = set()
    if flags:
        for f in flags:
            if isinstance(f, str):
                flag_set.add(f)
            elif isinstance(f, dict) and f.get("flag"):
                flag_set.add(f["flag"])

    for doc in documents:
        doc_class = doc.get("class") or doc.get("classified_as") or ""
        text = doc.get("text", "") or ""
        # Recompute per-doc flags to attach evidence and source_file
        from btp_engine.analysis.flag_detector import FlagDetector
        det = FlagDetector()
        per_doc_flags = det.detect(text, doc_class)
        for fl in per_doc_flags:
            name = fl["flag"]
            if name == "exclude_advisory_from_tasks":
                continue  # advisory marker, not a task
            spec = FLAG_TO_TASK.get(name)
            if not spec:
                continue
            tasks.append({
                "title": spec["title"],
                "name": spec["title"],
                "priority": spec["priority"],
                "source_file": doc.get("filename"),
                "source_class": doc_class,
                "flags": [name],
                "evidence": _excerpt(text, fl.get("matched_text", name)),
                "dst_mapping": list(spec["ft"]),
                "confidence": 0.9,
            })

    return tasks


def merge_similar_tasks(tasks: List[Dict]) -> List[Dict]:
    """Merge by (title, source_file). Combine flags/dst_mapping."""
    by_key: Dict = {}
    order: List = []
    for t in tasks:
        key = (t.get("title"), t.get("source_file"))
        if key not in by_key:
            by_key[key] = {
                **t,
                "flags": list(t.get("flags", []) or []),
                "dst_mapping": list(t.get("dst_mapping", []) or []),
            }
            order.append(key)
        else:
            cur = by_key[key]
            for fl in t.get("flags", []) or []:
                if fl not in cur["flags"]:
                    cur["flags"].append(fl)
            for ft in t.get("dst_mapping", []) or []:
                if ft not in cur["dst_mapping"]:
                    cur["dst_mapping"].append(ft)
    return [by_key[k] for k in order]
