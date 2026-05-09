"""JSON report generation."""

import json
from typing import Dict
from datetime import datetime


def generate_json_report(data: Dict, output_path: str):
    """
    Generate JSON report.
    
    Args:
        data: Report data
        output_path: Path to save JSON file
    """
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "data": data
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
