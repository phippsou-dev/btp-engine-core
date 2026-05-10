#!/usr/bin/env python3
"""BTP Engine Core - Main runner script.

Usage:
    python scripts/run_engine.py --input <path> --output <path> --dry-run
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from btp_engine.extraction import extract_pdf_text
from btp_engine.classification import classify_document
from btp_engine.analysis import detect_problems, detect_expert_flags
from btp_engine.tasks import generate_tasks, merge_similar_tasks
from btp_engine.dst import map_to_dst
from btp_engine.scoring import score_quality
from btp_engine.guardrails import CostTracker, get_guardrail_status
from btp_engine.reporting import (
    generate_json_report,
    generate_csv_report,
    generate_markdown_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="BTP Engine Core")
    parser.add_argument("--input", required=True, help="Input directory or PDF file")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode (required)")
    args = parser.parse_args()

    if not args.dry_run:
        print("ERROR: --dry-run is required (no production mode yet)")
        return 2

    cost_tracker = CostTracker()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input path not found: {input_path}")
        return 2

    pdf_files = []
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        pdf_files = [input_path]
    elif input_path.is_dir():
        pdf_files = sorted(input_path.glob("**/*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")

    documents = []
    extraction_report = []
    classification_report = []

    for pdf_file in pdf_files:
        print(f"  Processing: {pdf_file.name}")
        extraction = extract_pdf_text(str(pdf_file))
        classification = classify_document(extraction["filename"], extraction["text"])
        doc = {**extraction, **classification}
        documents.append(doc)
        extraction_report.append({
            "filename": extraction["filename"],
            "sha256": extraction["sha256"],
            "page_count": extraction["page_count"],
            "native_chars": extraction["native_chars"],
            "ocr_executed": extraction["ocr_executed"],
            "ocr_chars": extraction["ocr_chars"],
        })
        classification_report.append({
            "filename": extraction["filename"],
            "class": classification["class"],
            "confidence": classification["confidence"],
            "scores": classification["scores"],
        })

    all_problems = []
    all_flags = set()
    flags_by_doc = {}
    for doc in documents:
        problems = detect_problems(doc["text"], doc.get("class"))
        all_problems.extend(problems)
        flags = detect_expert_flags(doc["text"], doc.get("class"))
        flags_by_doc[doc["filename"]] = sorted(flags)
        all_flags.update(flags)

    # Per-doc audit (expected vs found)
    from btp_engine.analysis.flag_detector import compute_flag_audit
    per_doc = []
    for doc, ext in zip(documents, extraction_report):
        fname = doc["filename"]
        found = set(flags_by_doc.get(fname, []))
        audit = compute_flag_audit(fname, found, doc.get("text", ""))
        per_doc.append({
            "filename": fname,
            "classified_as": doc.get("class"),
            "ocr_executed": ext["ocr_executed"],
            "ocr_chars": ext["ocr_chars"],
            "critical_flags_found": sorted(found),
            "missing_expected_flags": audit["missing_expected_flags"],
            "optional_absent_from_source": audit["optional_absent_from_source"],
        })

    print(f"Detected {len(all_problems)} problems, {len(all_flags)} flags")

    tasks = generate_tasks(all_problems, all_flags, documents)
    tasks = merge_similar_tasks(tasks)
    print(f"Generated {len(tasks)} task candidates")

    dst_mapping = map_to_dst(tasks, dry_run=True)
    quality = score_quality(tasks, documents)
    guardrails = get_guardrail_status()

    # Outputs
    inventory = {
        "pdf_count": len(documents),
        "documents": [
            {k: v for k, v in d.items() if k != "text"} for d in documents
        ],
    }
    generate_json_report(inventory, output_dir / "inventory.json")
    generate_json_report({"documents": extraction_report}, output_dir / "extraction_report.json")
    generate_json_report({"documents": classification_report}, output_dir / "classification_report.json")
    generate_json_report(
        {"problems": all_problems, "flags_by_doc": flags_by_doc},
        output_dir / "problems.json",
    )
    generate_json_report({"tasks": tasks, "count": len(tasks)}, output_dir / "candidate_tasks.json")
    generate_csv_report(tasks, output_dir / "candidate_tasks.csv")
    generate_json_report(dst_mapping, output_dir / "dst_mapping_report.json")
    generate_json_report(quality, output_dir / "quality_score.json")
    generate_json_report(guardrails, output_dir / "guardrails_report.json")
    generate_json_report({"per_doc": per_doc}, output_dir / "per_doc.json")
    generate_markdown_report(documents, tasks, quality, guardrails, output_dir / "final_report.md")

    print(f"Pipeline complete. Output: {output_dir} / cost: ${cost_tracker.get_cost():.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
