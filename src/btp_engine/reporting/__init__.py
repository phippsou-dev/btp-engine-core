"""Reporting module - exposes class API and functional wrappers."""

import csv
import json
from io import StringIO
from pathlib import Path
from typing import Dict, List

from .json_reporter import JSONReporter
from .csv_reporter import CSVReporter
from .markdown_reporter import MarkdownReporter

__all__ = [
    "JSONReporter",
    "CSVReporter",
    "MarkdownReporter",
    "generate_json_report",
    "generate_csv_report",
    "generate_markdown_report",
]


def generate_json_report(data, output_path) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    p.write_text(txt, encoding="utf-8")
    return txt


def generate_csv_report(tasks: List[Dict], output_path) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "title", "priority", "source_file", "source_class",
        "flags", "dst_mapping", "evidence", "confidence",
    ]
    out = StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for t in tasks or []:
        row = dict(t)
        if isinstance(row.get("flags"), list):
            row["flags"] = "|".join(row["flags"])
        if isinstance(row.get("dst_mapping"), list):
            row["dst_mapping"] = "|".join(row["dst_mapping"])
        if not row.get("title"):
            row["title"] = t.get("name", "")
        writer.writerow({k: row.get(k, "") for k in fieldnames})
    text = out.getvalue()
    # UTF-8-SIG so Excel reads accents correctly
    p.write_text(text, encoding="utf-8-sig")
    return text


def generate_markdown_report(documents, tasks, quality, guardrails, output_path) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# BTP Engine Core - Final Report")
    lines.append("")
    lines.append("## Documents")
    for d in documents or []:
        lines.append(
            f"- **{d.get('filename')}** — class=`{d.get('class')}` "
            f"native_chars={d.get('native_chars')} ocr={d.get('ocr_executed')} "
            f"ocr_chars={d.get('ocr_chars')} pages={d.get('page_count')}"
        )
    lines.append("")
    lines.append(f"## Tasks ({len(tasks or [])})")
    for t in tasks or []:
        lines.append(
            f"- [{t.get('priority','?').upper()}] {t.get('title') or t.get('name')} "
            f"— src=`{t.get('source_file')}` flags=`{','.join(t.get('flags', []) or [])}` "
            f"FT=`{','.join(t.get('dst_mapping', []) or [])}`"
        )
    lines.append("")
    lines.append("## Quality")
    if quality:
        for k, v in quality.items():
            lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Guardrails")
    if guardrails:
        for k, v in guardrails.items():
            lines.append(f"- {k}: {v}")
    text = "\n".join(lines) + "\n"
    p.write_text(text, encoding="utf-8")
    return text
