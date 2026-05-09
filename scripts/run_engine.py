#!/usr/bin/env python3
"""
BTP Engine Core - Main runner script.

Usage:
    python scripts/run_engine.py --input <path> --output <path> --dry-run
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from btp_engine.extraction import extract_pdf_text
from btp_engine.classification import classify_document
from btp_engine.analysis import detect_problems, detect_expert_flags
from btp_engine.tasks import generate_tasks, merge_similar_tasks
from btp_engine.dst import map_to_dst
from btp_engine.scoring import score_quality, BaselineValidator
from btp_engine.guardrails import check_guardrails, CostTracker, get_guardrail_status
from btp_engine.reporting import generate_json_report, generate_csv_report, generate_markdown_report


def main():
    parser = argparse.ArgumentParser(description="BTP Engine Core")
    parser.add_argument("--input", required=True, help="Input directory or ZIP file")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode (required)")
    
    args = parser.parse_args()
    
    if not args.dry_run:
        print("ERROR: --dry-run is required (no production mode yet)")
        sys.exit(1)
    
    # Initialize
    cost_tracker = CostTracker()
    validator = BaselineValidator()
    
    # Check guardrails
    print("✓ Guardrails check...")
    try:
        check_guardrails("openai_call")  # Should fail
        print("ERROR: Guardrails failed to block OpenAI call")
        sys.exit(1)
    except Exception:
        pass  # Expected
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process input
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"ERROR: Input path not found: {input_path}")
        sys.exit(1)
    
    # Find PDFs
    pdf_files = []
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        pdf_files = [input_path]
    elif input_path.is_dir():
        pdf_files = list(input_path.glob("**/*.pdf"))
    
    print(f"✓ Found {len(pdf_files)} PDF files")
    
    # Extract and classify
    documents = []
    for pdf_file in pdf_files:
        print(f"  Processing: {pdf_file.name}")
        
        # Extract
        extraction = extract_pdf_text(str(pdf_file))
        
        # Classify
        classification = classify_document(
            extraction["filename"],
            extraction["text"]
        )
        
        # Merge results
        doc = {**extraction, **classification}
        documents.append(doc)
    
    print(f"✓ Extracted and classified {len(documents)} documents")
    
    # Analyze
    all_problems = []
    all_flags = set()
    
    for doc in documents:
        problems = detect_problems(doc["text"], doc.get("class"))
        all_problems.extend(problems)
        
        flags = detect_expert_flags(doc["text"], doc.get("class"))
        all_flags.update(flags)
    
    print(f"✓ Detected {len(all_problems)} problems")
    print(f"✓ Detected {len(all_flags)} expert flags")
    
    # Generate tasks
    tasks = generate_tasks(all_problems, all_flags, documents)
    tasks = merge_similar_tasks(tasks)
    
    print(f"✓ Generated {len(tasks)} task candidates")
    
    # Map to DST (dry-run)
    dst_mapping = map_to_dst(tasks, dry_run=True)
    
    print(f"✓ Mapped to DST (dry-run)")
    
    # Validate baselines
    for task in tasks:
        validator.validate_task_baseline(task, documents)
    
    validation_summary = validator.get_summary()
    print(f"✓ Baseline validation: {validation_summary['pass']}/{validation_summary['total']} PASS")
    
    # Quality score
    quality = score_quality(tasks, documents)
    print(f"✓ Quality score: {quality['overall_score']:.1%} ({quality['grade']})")
    
    # Generate reports
    print("\n✓ Generating reports...")
    
    # JSON reports
    generate_json_report(
        {"documents": documents},
        output_dir / "inventory.json"
    )
    
    generate_json_report(
        {"tasks": tasks},
        output_dir / "candidate_tasks.json"
    )
    
    generate_json_report(
        dst_mapping,
        output_dir / "dst_mapping_report.json"
    )
    
    generate_json_report(
        quality,
        output_dir / "quality_score.json"
    )
    
    generate_json_report(
        get_guardrail_status(),
        output_dir / "guardrails_report.json"
    )
    
    # CSV report
    generate_csv_report(
        tasks,
        output_dir / "candidate_tasks.csv"
    )
    
    # Markdown report
    generate_markdown_report(
        documents,
        tasks,
        quality,
        get_guardrail_status(),
        output_dir / "final_report.md"
    )
    
    print(f"\n✅ Pipeline complete!")
    print(f"   Output: {output_dir}")
    print(f"   Cost: ${cost_tracker.get_total():.2f}")
    print(f"   Quality: {quality['overall_score']:.1%} ({quality['grade']})")


if __name__ == "__main__":
    main()
