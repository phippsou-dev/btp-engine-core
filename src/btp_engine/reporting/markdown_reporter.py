"""Markdown report generation."""

from typing import Dict, List
from pathlib import Path


class MarkdownReporter:
    """Generate Markdown reports."""
    
    @staticmethod
    def generate_summary(data: Dict, output_path: str = None) -> str:
        """Generate summary report in Markdown."""
        lines = [
            "# BTP Engine Analysis Report",
            "",
            f"## Document: {data.get('document', 'Unknown')}",
            "",
            f"**Type:** {data.get('type', 'unknown')}",
            f"**Confidence:** {data.get('confidence', 0):.0%}",
            f"**Priority:** {data.get('priority', 'N/A')}",
            "",
        ]
        
        if "problems" in data and data["problems"]:
            lines.extend([
                "## Problems Detected",
                "",
            ])
            for problem in data["problems"]:
                severity = problem.get("severity", "unknown")
                desc = problem.get("description", "No description")
                lines.append(f"- **{severity.upper()}**: {desc}")
            lines.append("")
        
        if "tasks" in data and data["tasks"]:
            lines.extend([
                "## Generated Tasks",
                "",
            ])
            for task in data["tasks"]:
                priority = task.get("priority", "medium")
                name = task.get("name", "Unnamed task")
                lines.append(f"- [{priority.upper()}] {name}")
            lines.append("")
        
        if "scores" in data:
            lines.extend([
                "## Quality Scores",
                "",
            ])
            scores = data["scores"]
            for metric, score in scores.items():
                lines.append(f"- **{metric}**: {score}")
            lines.append("")
        
        markdown = "\n".join(lines)
        
        if output_path:
            Path(output_path).write_text(markdown, encoding="utf-8")
        
        return markdown