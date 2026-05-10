"""Analysis module - Problem detection and flagging."""

from typing import Dict, List, Optional, Set

from .problem_detector import ProblemDetector
from .flag_detector import FlagDetector, detect_expert_flags_for_class
from .expert_rules import ExpertRules

__all__ = [
    "ProblemDetector",
    "FlagDetector",
    "ExpertRules",
    "detect_problems",
    "detect_expert_flags",
]


def detect_problems(text: str, doc_class: Optional[str] = None) -> List[Dict]:
    detector = ProblemDetector()
    # ProblemDetector.detect signature is (text, doc_type)
    return detector.detect(text or "", doc_class or "")


def detect_expert_flags(text: str, doc_class: Optional[str] = None) -> Set[str]:
    return detect_expert_flags_for_class(text or "", doc_class)
