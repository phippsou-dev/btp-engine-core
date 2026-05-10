"""Flag detector for BTP documents - Phase 6 business flags."""

import re
from typing import Dict, List, Optional, Set


# Per-class flag dictionary. Each entry: name -> list of regex patterns.
FLAGS_BY_CLASS: Dict[str, Dict[str, List[str]]] = {
    "NOTICE_SECURITE_HABITATION": {
        "permis_construire_coche": [r"permis\s+de\s+construire"],
        "etablissement_identifie": [r"appartement", r"immeuble"],
        "demandeur": [r"promouvoir\s+invest|demandeur"],
        "adresse": [r"rue\s+des\s+balances|16\s+rue"],
        "commune": [r"34500|b[ée]ziers"],
        "maitre_oeuvre": [r"2a2m|ma[îi]tre\s+d['’ ]?oeuvre|architecte"],
        "batiments_habitation": [r"b[âa]timents?\s+d['’ ]habitation"],
        "cages_escalier": [r"cages?\s+d['’ ]?escalier"],
        "desenfumage": [r"d[ée]senfumage"],
        "coupe_feu": [r"coupe[- ]feu|\bcf\s*1?h?\b"],
    },
    "DPE_PROJETE": {
        "needs_thermique_DPE": [r"\bdpe\b|performance\s+[ée]nerg[ée]tique"],
        "PAC_air_air": [r"pac\s+air\s*/\s*air|pompe\s+[àa]\s+chaleur"],
        "chauffe_eau_thermodynamique": [r"chauffe[- ]eau\s+thermodynamique"],
        "VMC_Hygro_B": [r"vmc\s+sf?\s*hygro\s*b|hygro\s*b"],
        "isolation_R_3_7": [r"r\s*=\s*3[,\.]7|r\s*≥\s*3[,\.]7"],
        "fenetres_double_vitrage": [r"double\s+vitrage|fen[êe]tres?\s+performantes?"],
        # Includes explicit "Remplacer les portes par des menuiseries plus performantes" wording
        "portes_performantes": [
            r"portes?\s+performantes?",
            r"portes?\s+isolantes?",
            r"remplacer\s+les\s+portes",
            r"menuiseries\s+plus\s+performantes",
        ],
        "exclude_advisory_from_tasks": [r"conseils?\s+d['’ ]usage|recommandations?\s+d['’ ]usage"],
    },
    "EDL_AVANT_PROJET": {
        "local_commercial_non_visite": [r"local\s+commercial\s+(?:et\s+l['’]?\s*appartement\s+)?.{0,40}non\s+visit", r"local\s+commercial.{0,80}n['’ ]?(?:a|ont)\s+pas\s+pu\s+[êe]tre\s+visit"],
        "appartement_R1_non_visite": [
            r"appartement\s+(?:du\s+)?r\s*\+?\s*1.{0,60}n['’ ]?(?:a|ont)\s+pas\s+pu\s+[êe]tre\s+visit",
            r"appartement\s+r\s*\+?\s*1\s+non\s+visit",
        ],
        "PC_deja_realise": [r"permis\s+de\s+construire\s+d[ée]j[àa]\s+r[ée]alis", r"pc\s+d[ée]j[àa]\s+r[ée]alis", r"d[ée]j[àa]\s+r[ée]alis[ée]\s+par\s+confr"],
        "cheminees_plafonds_moulures": [r"chemin[ée]e", r"plafonds?\s+moulur"],
        "reseaux_fioul_gaz": [r"\bfioul\b", r"\bgaz\b"],
        "plancher_R4_affaisse": [
            r"plancher\s+r\s*\+?\s*4\s+affaiss",
            r"(?:quatri[èe]me\s+[ée]tage|r\s*\+?\s*4|toiture\s+du\s+r\s*\+?\s*4)[\s\S]{0,120}plancher[\s\S]{0,80}affaiss",
            r"plancher[\s\S]{0,80}affaiss[\s\S]{0,120}(?:quatri[èe]me|r\s*\+?\s*4)",
        ],
        # Accepts "envisager un plancher connecté" and direct mention.
        "plancher_connecte": [r"plancher\s+conn?ect", r"envisager\s+un\s+plancher\s+conn?ect"],
        "facade_fissuree": [r"fa[çc]ade\s+fissur", r"fa[çc]ade[\s\S]{0,120}fissur"],
        # Accepts OCR/typo "refort" as well as correct "renfort".
        "renfort_sous_toiture": [r"r[eé]n?fort\s+sous\s+toiture", r"pr[ée]voir\s+(?:un\s+)?r[eé]n?fort\s+sous\s+toiture"],
        "evacuations_amiante": [r"[ée]vacuations?\s+(?:en\s+)?amiante|d[ée]pose\s+amiante|r[ée]seaux\s+d['’ ]?[ée]vacuation\s+en\s+amiante"],
        "toiture_fibrociment_amiante": [r"toiture\s+fibrociment|fibrociment.*amiante"],
        # Multi-line / multi-word phrasing such as "doublage, isolant du mur périphérique
        # de la cage d'escalier pour assurer le coupe-feu".
        "coupe_feu_cage_escalier": [
            r"cage\s+d['’ ]?escalier[\s\S]{0,120}coupe[- ]feu",
            r"coupe[- ]feu[\s\S]{0,120}cage\s+d['’ ]?escalier",
        ],
        # Accepts "remplacement des portes palière en coupe-feu une heure" and CF1h shorthand.
        "portes_palieres_CF1h": [
            r"portes?\s+pali[èe]res?[\s\S]{0,80}(?:cf\s*1\s*h|coupe[- ]feu(?:\s+une\s+heure)?)",
            r"remplacement\s+des?\s+portes?\s+pali[èe]res?",
        ],
        "lanterneau_desenfumage": [r"lanterneau|d[ée]senfumage"],
        "needs_diagnostic": [r"diagnostic|expertise"],
        "needs_BET": [r"\bbet\b|bureau\s+d['’ ]?[ée]tudes?"],
        "needs_securite_incendie": [r"s[ée]curit[ée]\s+incendie|coupe[- ]feu"],
        "needs_ABF": [r"\babf\b|architecte\s+des\s+b[âa]timents"],
    },
    "PLAN_GRAPHIC_PC_FACADES": {
        "PC_22T0205": [r"22\s*t\s*0?2?0?5|pc\s+n[°o]?\s*22"],
        "renovation_facades": [r"r[ée]novation\s+fa[çc]ades?", r"ravalement\s+(?:des?\s+)?fa[çc]ades?"],
        "descentes_EP": [r"descentes?\s+ep|eaux\s+pluviales"],
        "enduit_ciment_decroute": [r"enduit\s+ciment.*d[ée]cro[ûu]t|d[ée]cro[ûu]t.*ciment"],
        "enduit_chaux_ton_pierre": [r"enduit.*chaux.*pierre|chaux\s+ton\s+pierre"],
        "chainages_angles": [r"cha[îi]nages?\s+d['’ ]?angles?"],
        "corniche_genoises": [r"\bcorniche\b", r"\bg[ée]noises?\b"],
        "menuiseries_bois_R2_R3": [r"menuiseries\s+bois"],
        "menuiseries_PVC_R1_remplacees": [r"menuiseries\s+pvc"],
        "porte_acier_conservee": [r"porte\s+acier"],
        "lambrequins_non_conserves": [r"lambrequins"],
        "garde_corps_traites": [r"garde[- ]corps|ferronneries"],
        # Accepts OCR phrasings: "VITRINES DU COMMERCE EN RDC" /
        # "devantures ne seront pas traitées dans le cadre du ravalement" /
        # "demande spécifique de devantures par le futur commerçant locataire".
        "vitrines_RDC_exclues": [
            r"vitrines?\s+(?:du\s+commerce\s+)?en\s+rdc",
            r"vitrines?\s+du\s+commerce",
            r"devantures?\s+ne\s+seront\s+pas\s+trait",
            r"demande\s+sp[ée]cifique\s+de\s+devantures",
            r"vitrines?\s+rdc",
            r"rdc.{0,40}vitrines?",
        ],
    },
}


# Generic / legacy patterns kept for backward compat
LEGACY_PATTERNS = {
    "missing_signature": {"pattern": r"signature\s+manquante|non\s+signé|unsigned", "severity": "high"},
    "incomplete_data": {"pattern": r"incomplet|données\s+manquantes|missing\s+data", "severity": "medium"},
    "expired": {"pattern": r"expiré|périmé|expired", "severity": "high"},
    "non_compliant": {"pattern": r"non\s+conforme|not\s+compliant|violation", "severity": "critical"},
}


class FlagDetector:
    """Detect business flags in BTP documents."""

    FLAG_PATTERNS = LEGACY_PATTERNS  # backward compat for old tests

    def __init__(self):
        self.detected_flags: List[Dict] = []

    def detect(self, text: str, doc_class: Optional[str] = None) -> List[Dict]:
        """Detect flags. If doc_class is given, use class-specific dict.
        Otherwise fall back to legacy patterns."""
        self.detected_flags = []
        if not text:
            return []
        text_lc = text.lower()

        if doc_class and doc_class in FLAGS_BY_CLASS:
            for flag_name, patterns in FLAGS_BY_CLASS[doc_class].items():
                for pat in patterns:
                    m = re.search(pat, text_lc, re.IGNORECASE)
                    if m:
                        self.detected_flags.append({
                            "flag": flag_name,
                            "doc_class": doc_class,
                            "severity": "high",
                            "matched_text": m.group(0),
                            "position": m.start(),
                        })
                        break
        else:
            for flag_name, info in LEGACY_PATTERNS.items():
                for m in re.finditer(info["pattern"], text_lc, re.IGNORECASE):
                    self.detected_flags.append({
                        "flag": flag_name,
                        "severity": info["severity"],
                        "matched_text": m.group(0),
                        "position": m.start(),
                    })
        return self.detected_flags

    def get_critical_flags(self) -> List[Dict]:
        return [f for f in self.detected_flags if f.get("severity") == "critical"]


def detect_expert_flags_for_class(text: str, doc_class: Optional[str]) -> Set[str]:
    """Return set of flag names for a document of given class."""
    detector = FlagDetector()
    flags = detector.detect(text, doc_class)
    return {f["flag"] for f in flags}


# Expected flag sets per Phase 6 reference filename.
# Used by scripts/run_engine.py to compute missing_expected_flags.
EXPECTED_FLAGS_BY_FILENAME: Dict[str, Set[str]] = {
    "notice_securite_habitation.pdf": {
        "permis_construire_coche", "etablissement_identifie", "demandeur",
        "adresse", "commune", "maitre_oeuvre", "batiments_habitation",
        "cages_escalier", "desenfumage", "coupe_feu",
    },
    "dpe_projete_archi_home.pdf": {
        "needs_thermique_DPE", "PAC_air_air", "chauffe_eau_thermodynamique",
        "VMC_Hygro_B", "isolation_R_3_7", "fenetres_double_vitrage",
        "portes_performantes", "exclude_advisory_from_tasks",
    },
    "edl_projet_beziers.pdf": {
        "local_commercial_non_visite", "appartement_R1_non_visite",
        "PC_deja_realise", "plancher_R4_affaisse", "plancher_connecte",
        "facade_fissuree", "renfort_sous_toiture", "evacuations_amiante",
        "toiture_fibrociment_amiante", "coupe_feu_cage_escalier",
        "portes_palieres_CF1h", "lanterneau_desenfumage", "needs_ABF",
    },
    "pieces_pc_demande.pdf": {
        "PC_22T0205", "renovation_facades", "descentes_EP",
        "enduit_ciment_decroute", "enduit_chaux_ton_pierre",
        "chainages_angles", "corniche_genoises", "menuiseries_bois_R2_R3",
        "menuiseries_PVC_R1_remplacees", "porte_acier_conservee",
        "lambrequins_non_conserves", "garde_corps_traites",
        "vitrines_RDC_exclues",
    },
}

# Flags that may legitimately be absent if the source PDF does not reference
# them. They are reported as `optional_absent_from_source` instead of missing.
OPTIONAL_FLAGS_BY_FILENAME: Dict[str, Set[str]] = {
    "dpe_projete_archi_home.pdf": {"portes_performantes"},
}


def compute_flag_audit(filename: str, found: Set[str], text: str) -> Dict[str, List[str]]:
    """Return {missing_expected_flags, optional_absent_from_source} for a doc."""
    expected = EXPECTED_FLAGS_BY_FILENAME.get(filename, set())
    optional = OPTIONAL_FLAGS_BY_FILENAME.get(filename, set())
    missing = expected - set(found)
    optional_absent: Set[str] = set()
    text_lc = (text or "").lower()
    for opt in list(missing & optional):
        # Optional flags only marked absent if no triggering keyword in source.
        keywords = {
            "portes_performantes": ["porte", "menuiserie"],
        }.get(opt, [])
        if not any(k in text_lc for k in keywords):
            optional_absent.add(opt)
            missing.discard(opt)
    return {
        "missing_expected_flags": sorted(missing),
        "optional_absent_from_source": sorted(optional_absent),
    }
