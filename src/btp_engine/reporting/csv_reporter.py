"""CSV report generation."""

import csv
from typing import Dict, List
from pathlib import Path
from io import StringIO


class CSVReporter:
    """Generate CSV reports."""
    
    @staticmethod
    def generate_tasks_csv(tasks: List[Dict], output_path: str = None) -> str:
        """Generate CSV report for tasks."""
        output = StringIO()
        
        fieldnames = ["name", "priority", "description", "source"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for task in tasks:
            row = {k: task.get(k, "") for k in fieldnames}
            writer.writerow(row)
        
        csv_str = output.getvalue()
        
        if output_path:
            Path(output_path).write_text(csv_str, encoding="utf-8")
        
        return csv_str
    
    @staticmethod
    def generate_problems_csv(problems: List[Dict], output_path: str = None) -> str:
        """Generate CSV report for problems."""
        output = StringIO()
        
        fieldnames = ["severity", "description", "matched_text"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for problem in problems:
            row = {k: problem.get(k, "") for k in fieldnames}
            writer.writerow(row)
        
        csv_str = output.getvalue()
        
        if output_path:
            Path(output_path).write_text(csv_str, encoding="utf-8")
        
        return csv_str