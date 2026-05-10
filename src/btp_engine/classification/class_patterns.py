"""Classification patterns for BTP documents."""

from typing import Dict, List


class ClassificationPatterns:
    """Define patterns for document classification."""

    PATTERNS: Dict[str, List[str]] = {
        # Legacy generic types (kept for backward compat)
        "facture": [
            r"facture\s+n[°o]",
            r"invoice\s+number",
            r"montant\s+ht",
            r"montant\s+ttc",
            r"\btva\b",
        ],
        "devis": [
            r"devis\s+n[°o]",
            r"estimation",
            r"\bquote\b",
            r"prix\s+unitaire",
            r"total\s+estimatif",
        ],
        "plan": [
            r"plan\s+de\s+(?:masse|situation|coupe)",
            r"échelle\s+1\s*[:/]\s*\d",
            r"architectural\s+plan",
            r"blueprint",
        ],
        "permis": [
            r"permis\s+de\s+construire",
            r"building\s+permit",
            r"autorisation\s+d'urbanisme",
            r"déclaration\s+préalable",
        ],
        "rapport": [
            r"rapport\s+technique",
            r"technical\s+report",
            r"compte\s+rendu",
            r"\bexpertise\b",
        ],
        "contrat": [
            r"contrat\s+de\b",
            r"\bcontract\b",
            r"conditions\s+générales",
            r"signataires",
            r"stipulations",
        ],
        # Phase 6 business classes
        "NOTICE_SECURITE_HABITATION": [
            r"notice\s+descriptive\s+de\s+s[ée]curit[ée]",
            r"notice\s+de\s+s[ée]curit[ée]",
            r"b[âa]timents?\s+d['’ ]habitation",
            r"cages?\s+d['’ ]?escalier",
            r"d[ée]senfumage",
            r"coupe[- ]feu",
            r"cf\s*1\s*h",
            r"promouvoir\s+invest",
            r"rue\s+des\s+balances",
            r"34500",
            r"b[ée]ziers",
            r"2a2m\s+architecture",
        ],
        "DPE_PROJETE": [
            r"diagnostic\s+de\s+performance\s+[ée]nerg[ée]tique",
            r"\bdpe\b",
            r"dpe\s+projet[ée]",
            r"apr[èe]s\s+travaux",
            r"vmc\s+sf?\s*hygro\s*b",
            r"pac\s+air\s*/\s*air",
            r"chauffe[- ]eau\s+thermodynamique",
            r"r\s*=\s*3[,\.]7",
            r"double\s+vitrage",
        ],
        "EDL_AVANT_PROJET": [
            r"\bedl\b\s*projet",
            r"\bedl\b",
            r"[ée]tat\s+des\s+lieux",
            r"local\s+commercial\s+non\s+visit[ée]",
            r"appartement\s+r\+1\s+non\s+visit[ée]",
            r"plancher\s+r\+4\s+affaiss",
            r"plancher\s+connect",
            r"fa[çc]ade\s+fissur",
            r"renfort\s+sous\s+toiture",
            r"toiture\s+fibrociment",
            r"\bamiante\b",
            r"\babf\b",
            r"\bfioul\b",
            r"plafonds?\s+moulur",
            r"chemin[ée]es",
            r"lanterneau",
        ],
        "PLAN_GRAPHIC_PC_FACADES": [
            r"pc\s*n[°o]?\s*22\s*t\s*0?2?0?5",
            r"22t0205",
            r"permis\s+modificatif",
            r"coupe\s+et\s+fa[çc]ades?",
            r"r[ée]novation\s+fa[çc]ades?",
            r"descentes?\s+ep",
            r"enduit\s+ciment",
            r"enduit\s+(?:100\s*%\s+)?chaux",
            r"cha[îi]nages?\s+d['’ ]?angles?",
            r"\bcorniche\b",
            r"\bg[ée]noises?\b",
            r"menuiseries\s+bois",
            r"menuiseries\s+pvc",
            r"lambrequins",
            r"garde[- ]corps",
            r"ferronneries",
            r"vitrines\s+rdc",
        ],
    }

    @classmethod
    def get_patterns(cls, doc_type: str) -> List[str]:
        return cls.PATTERNS.get(doc_type, [])

    @classmethod
    def all_types(cls) -> List[str]:
        return list(cls.PATTERNS.keys())
