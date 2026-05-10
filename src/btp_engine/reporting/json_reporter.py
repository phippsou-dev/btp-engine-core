"""JSON report generation."""

import json
from typing import Dict, Any
from pathlib import Path


class JSONReporter:
    """Generate JSON reports."""
    
    @staticmethod
    def generate(data: Dict[str, Any], output_path: str = None) -> str:
        """Generate JSON report."""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if output_path:
            Path(output_path).write_text(json_str, encoding="utf-8")
        
        return json_str
    
    @staticmethod
    def generate_compact(data: Dict[str, Any]) -> str:
        """Generate compact JSON report."""
        return json.dumps(data, ensure_ascii=False)