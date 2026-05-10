"""Phase 6 regression tests."""
import subprocess
import sys
from pathlib import Path

import pytest


def test_pytest_runs_without_pythonpath():
    """conftest.py + pyproject.toml ensure btp_engine is importable directly."""
    import btp_engine  # noqa
    assert hasattr(btp_engine, "__version__")


def test_reporting_imports():
    from btp_engine.reporting import (
        JSONReporter, CSVReporter, MarkdownReporter,
        generate_json_report, generate_csv_report, generate_markdown_report,
    )
    assert callable(generate_json_report)
    assert callable(generate_csv_report)
    assert callable(generate_markdown_report)


def test_run_engine_imports():
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_engine.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr


def test_ocr_fallback_callable():
    from btp_engine.extraction import ocr_pdf_local, needs_ocr_fallback
    assert callable(ocr_pdf_local)
    assert needs_ocr_fallback("") is True
    assert needs_ocr_fallback("a" * 1000) is False


def test_classifier_recognises_phase6_classes():
    from btp_engine.classification import classify_document
    samples = {
        "notice_securite_habitation.pdf":
            "NOTICE DESCRIPTIVE DE SECURITE — Bâtiments d'habitation\n"
            "Permis de construire — Promouvoir Invest — 16 Rue des Balances 34500 Béziers\n"
            "Cages d'escalier, désenfumage, coupe-feu CF1h",
        "dpe_projete_archi_home.pdf":
            "Diagnostic de performance énergétique - DPE PROJETE APRES TRAVAUX\n"
            "VMC SF Hygro B après 2012, PAC air/air, chauffe-eau thermodynamique\n"
            "R=3,7 m².K/W, double vitrage",
        "edl_projet_beziers.pdf":
            "EDL PROJET - Description du bâtiment\n"
            "Local commercial non visité, appartement R+1 non visité, ABF, fioul, gaz,\n"
            "plancher R+4 affaissé, façade fissurée, toiture fibrociment amiante,\n"
            "coupe-feu cage escalier, portes palières CF 1h, lanterneau désenfumage",
        "pieces_pc_demande.pdf":
            "PC n°22T0205 PERMIS MODIFICATIF — COUPE et FACADES\n"
            "rénovation façades, descentes EP, enduit ciment à décrouter,\n"
            "enduit 100% chaux ton pierre, chaînages d'angles, corniche, génoises,\n"
            "menuiseries bois R+2/R+3, menuiseries PVC R+1, lambrequins, garde-corps",
    }
    expected = {
        "notice_securite_habitation.pdf": "NOTICE_SECURITE_HABITATION",
        "dpe_projete_archi_home.pdf": "DPE_PROJETE",
        "edl_projet_beziers.pdf": "EDL_AVANT_PROJET",
        "pieces_pc_demande.pdf": "PLAN_GRAPHIC_PC_FACADES",
    }
    for fname, txt in samples.items():
        result = classify_document(fname, txt)
        assert result["class"] == expected[fname], f"{fname}: got {result['class']}"


def test_flag_detector_critical_flags():
    from btp_engine.analysis import detect_expert_flags
    edl_text = (
        "plancher R+4 affaissé, toiture fibrociment amiante, "
        "ABF, lanterneau désenfumage"
    )
    flags = detect_expert_flags(edl_text, "EDL_AVANT_PROJET")
    assert "plancher_R4_affaisse" in flags
    assert "toiture_fibrociment_amiante" in flags
    assert "needs_ABF" in flags

    dpe_text = "VMC SF Hygro B, PAC air/air, R=3,7 m².K/W, double vitrage"
    dpe_flags = detect_expert_flags(dpe_text, "DPE_PROJETE")
    assert "VMC_Hygro_B" in dpe_flags
    assert "PAC_air_air" in dpe_flags
    assert "isolation_R_3_7" in dpe_flags


def test_dpe_advisory_excluded_from_tasks():
    from btp_engine.tasks import generate_tasks
    docs = [{
        "filename": "dpe.pdf",
        "class": "DPE_PROJETE",
        "text": (
            "DPE projeté. Conseils d'usage: aérer 5 min/jour. "
            "PAC air/air, VMC SF Hygro B, R=3,7"
        ),
    }]
    tasks = generate_tasks([], set(), docs)
    titles = [t["title"] for t in tasks]
    assert any("PAC air/air" in t for t in titles)
    assert all("conseils" not in t.lower() and "aérer" not in t.lower() for t in titles)
