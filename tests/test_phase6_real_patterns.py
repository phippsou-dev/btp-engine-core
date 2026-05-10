"""Phase 6 strict pattern regression — real OCR/text wording."""
from btp_engine.analysis import detect_expert_flags
from btp_engine.analysis.flag_detector import compute_flag_audit


def test_phase6_real_patterns_edl_residual_flags():
    text = (
        "Le Local commercial et l’appartement du R+1 n’ont pas pu être visités.\n"
        "Permis de construire déjà réalisé par confrère.\n"
        "envisager un plancher connecté sur le dernier étage.\n"
        "Par sécurité prévoir un refort sous toiture avant démontage.\n"
        "Au quatrième étage, le plancher présente des gros affaissement.\n"
        "Le haut de la façade sur rue présente des grosses fissures.\n"
        "Les réseaux d’évacuation en amiante visibles seront encoffrés.\n"
        "doublage, isolant du mur périphérique de la cage d’escalier "
        "pour assurer le coupe-feu aux normes.\n"
        "remplacement des portes palière en coupe-feu une heure.\n"
    )
    flags = detect_expert_flags(text, "EDL_AVANT_PROJET")
    for expected in [
        "appartement_R1_non_visite",
        "PC_deja_realise",
        "plancher_connecte",
        "renfort_sous_toiture",
        "plancher_R4_affaisse",
        "facade_fissuree",
        "evacuations_amiante",
        "coupe_feu_cage_escalier",
        "portes_palieres_CF1h",
        "local_commercial_non_visite",
    ]:
        assert expected in flags, f"missing flag {expected}; got {sorted(flags)}"


def test_phase6_real_patterns_pc_vitrines():
    text = (
        "LES VITRINES DU COMMERCE EN RDC: les devantures ne seront pas "
        "traitées dans le cadre du ravalement des façades et feront l'objet "
        "d'une demande spécifique de devantures par le futur commerçant "
        "locataire."
    )
    flags = detect_expert_flags(text, "PLAN_GRAPHIC_PC_FACADES")
    assert "vitrines_RDC_exclues" in flags
    assert "renovation_facades" in flags


def test_phase6_dpe_portes_performantes_optional_if_absent():
    # Source mentions portes -> not absent; portes_performantes expected to match
    dpe_with = "Remplacer les portes par des menuiseries plus performantes."
    flags_with = detect_expert_flags(dpe_with, "DPE_PROJETE")
    assert "portes_performantes" in flags_with

    # Source without portes/menuiserie -> optional_absent_from_source path
    dpe_without = "VMC SF Hygro B et PAC air/air uniquement."
    flags_without = detect_expert_flags(dpe_without, "DPE_PROJETE")
    audit = compute_flag_audit(
        "dpe_projete_archi_home.pdf", set(flags_without), dpe_without
    )
    assert "portes_performantes" not in audit["missing_expected_flags"]
    assert "portes_performantes" in audit["optional_absent_from_source"]
