"""CSV report generation with UTF-8-SIG encoding."""

import csv
from typing import List, Dict


def generate_csv_report(tasks: List[Dict], output_path: str):
    """
    Generate CSV report with UTF-8-SIG encoding (Excel-compatible).
    
    Args:
        tasks: List of tasks
        output_path: Path to save CSV file
    """
    if not tasks:
        return
    
    # Define columns
    columns = [
        "candidate_id",
        "title",
        "description",
        "category",
        "severity",
        "confidence",
        "dst_families",
        "expert_flags",
        "human_review_required",
        "source_files",
    ]
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        
        for task in tasks:
            # Convert lists to strings
            row = task.copy()
            if "dst_families" in row and isinstance(row["dst_families"], list):
                row["dst_families"] = ", ".join(row["dst_families"])
            if "expert_flags" in row and isinstance(row["expert_flags"], list):
                row["expert_flags"] = ", ".join(row["expert_flags"])
            if "source_files" in row and isinstance(row["source_files"], list):
                row["source_files"] = ", ".join(row["source_files"])
            
            writer.writerow(row)
