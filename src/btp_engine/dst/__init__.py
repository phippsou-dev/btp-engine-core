"""DST module - mapping tasks to FT codes (dry-run only)."""

from typing import Dict, List

from .dst_mapper import DSTMapper
from .dst_rules import DSTRules

__all__ = ["DSTMapper", "DSTRules", "map_to_dst"]


def map_to_dst(tasks: List[Dict], dry_run: bool = True) -> Dict:
    """Aggregate task -> FT mapping. NEVER pushes to a real DST."""
    if not dry_run:
        raise RuntimeError("DST push is forbidden by guardrails (dry_run=True only)")
    mappings: List[Dict] = []
    by_ft: Dict[str, int] = {}
    for t in tasks:
        fts = t.get("dst_mapping", []) or []
        mappings.append({
            "task_title": t.get("title") or t.get("name"),
            "source_file": t.get("source_file"),
            "ft_codes": list(fts),
            "flags": list(t.get("flags", []) or []),
        })
        for ft in fts:
            by_ft[ft] = by_ft.get(ft, 0) + 1
    return {
        "dry_run": True,
        "pushed": False,
        "count": len(mappings),
        "mappings": mappings,
        "by_ft": by_ft,
    }
