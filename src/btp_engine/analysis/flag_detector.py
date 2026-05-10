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
        "portes_performantes": [r"portes?\s+performantes?|portes?\s+isolantes?"],
        "exclude_advisory_from_tasks": [r"conseils?\s+d['’ ]usage|recommandations?\s+d['’ ]usage"],
    },
    "EDL_AVANT_PROJET": {
        "local_commercial_non_visite": [r"local\s+commercial\s+non\s+visit"],
        "appartement_R1_non_visite": [r"appartement\s+r\s*\+?\s*1\s+non\s+visit"],
        "PC_deja_realise": [r"permis.*d[ée]j[àa]\s+r[ée]alis|pc\s+d[ée]j[àa]"],
        "cheminees_plafonds_moulures": [r"chemin[ée]e", r"plafonds?\s+moulur"],
        "reseaux_fioul_gaz": [r"\bfioul\b", r"\bgaz\b"],
        "plancher_R4_affaisse": [r"plancher\s+r\s*\+?\s*4\s+affaiss"],
        "plancher_connecte": [r"plancher\s+connect"],
        "facade_fissuree": [r"fa[çc]ade\s+fissur"],
        "renfort_sous_toiture": [r"renfort\s+sous\s+toiture"],
        "evacuations_amiante": [r"[ée]vacuations?\s+amiante|d[ée]pose\s+amiante"],
        "toiture_fibrociment_amiante": [r"toiture\s+fibrociment|fibrociment.*amiante"],
        "coupe_feu_cage_escalier": [r"coupe[- ]feu.*cage|cage.*coupe[- ]feu"],
        "portes_palieres_CF1h": [r"portes?\s+pali[èe]res?.*(?:cf\s*1\s*h|coupe[- ]feu)"],
        "lanterneau_desenfumage": [r"lanterneau|d[ée]senfumage"],
        "needs_diagnostic": [r"diagnostic|expertise"],
        "needs_BET": [r"\bbet\b|bureau\s+d['’ ]?[ée]tudes?"],
        "needs_securite_incendie": [r"s[ée]curit[ée]\s+incendie|coupe[- ]feu"],
        "needs_ABF": [r"\babf\b|architecte\s+des\s+b[âa]timents"],
    },
    "PLAN_GRAPHIC_PC_FACADES": {
        "PC_22T0205": [r"22\s*t\s*0?2?0?5|pc\s+n[°o]?\s*22"],
        "renovation_facades": [r"r[ée]novation\s+fa[çc]ades?"],
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
        "vitrines_RDC_exclues": [r"vitrines\s+rdc|rdc.*vitrines?"],
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
