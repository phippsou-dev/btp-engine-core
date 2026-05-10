"""Scoring module."""

from typing import Dict, List

from .quality_scorer import QualityScorer
from .baseline_validator import BaselineValidator

__all__ = ["QualityScorer", "BaselineValidator", "score_quality"]


def score_quality(tasks: List[Dict], documents: List[Dict]) -> Dict:
    n_docs = len(documents) or 1
    n_classed = sum(1 for d in documents if (d.get("class") or "").lower() not in ("", "unknown"))
    n_tasks = len(tasks)
    classification_rate = n_classed / n_docs
    task_coverage = min(1.0, n_tasks / max(1, n_docs * 5))
    overall = round(0.5 * classification_rate + 0.5 * task_coverage, 3)
    if overall >= 0.85:
        grade = "A"
    elif overall >= 0.7:
        grade = "B"
    elif overall >= 0.5:
        grade = "C"
    else:
        grade = "D"
    return {
        "overall_score": overall,
        "grade": grade,
        "classification_rate": round(classification_rate, 3),
        "task_coverage": round(task_coverage, 3),
        "documents_count": n_docs,
        "classified_count": n_classed,
        "tasks_count": n_tasks,
    }
