"""Markdown report generation."""

from typing import Dict, List
from datetime import datetime


def generate_markdown_report(
    documents: List[Dict],
    tasks: List[Dict],
    quality_score: Dict,
    guardrails: Dict,
    output_path: str
):
    """
    Generate comprehensive Markdown report.
    
    Args:
        documents: List of processed documents
        tasks: List of task candidates
        quality_score: Quality score data
        guardrails: Guardrails report
        output_path: Path to save Markdown file
    """
    lines = []
    
    # Header
    lines.append("# BTP Engine Core - Rapport d'Exécution")
    lines.append(f"\n**Généré le** : {datetime.utcnow().isoformat()}")
    lines.append(f"\n**Version** : 0.1.0\n")
    
    # Executive Summary
    lines.append("## Synthèse Exécutive\n")
    lines.append(f"- **Documents traités** : {len(documents)}")
    lines.append(f"- **Tâches candidates générées** : {len(tasks)}")
    lines.append(f"- **Score qualité global** : {quality_score.get('overall_score', 0):.1%} ({quality_score.get('grade', 'N/A')})")
    lines.append(f"- **Coût total** : ${guardrails.get('total_cost', 0):.2f}\n")
    
    # Guardrails Status
    lines.append("## État des Guardrails\n")
    lines.append("| Guardrail | État |")
    lines.append("|-----------|------|")
    for key, value in guardrails.items():
        if key.endswith("_ENABLED") or key.startswith("MAX_"):
            status = "✅ OK" if not value else "❌ ACTIVÉ"
            if key.startswith("MAX_"):
                status = f"✅ {value}"
            lines.append(f"| {key} | {status} |")
    lines.append("")
    
    # Documents
    lines.append("## Documents Traités\n")
    if documents:
        lines.append("| Fichier | Classe | Confiance | Pages |")
        lines.append("|---------|--------|-----------|-------|")
        for doc in documents[:20]:  # Limit to 20
            filename = doc.get("filename", "N/A")
            doc_class = doc.get("class", "UNKNOWN")
            confidence = doc.get("confidence", 0.0)
            pages = doc.get("pages", 0)
            lines.append(f"| {filename} | {doc_class} | {confidence:.1%} | {pages} |")
        if len(documents) > 20:
            lines.append(f"\n*... et {len(documents) - 20} autres documents*")
    else:
        lines.append("*Aucun document traité*")
    lines.append("")
    
    # Tasks
    lines.append("## Tâches Candidates\n")
    if tasks:
        lines.append("| ID | Titre | Catégorie | Confiance | DST |")
        lines.append("|----|-------|-----------|-----------|-----|")
        for task in tasks[:20]:  # Limit to 20
            task_id = task.get("candidate_id", "N/A")[:8]
            title = task.get("title", "N/A")
            category = task.get("category", "N/A")
            confidence = task.get("confidence", 0.0)
            dst = ", ".join(task.get("dst_mapping", [])[:2])
            lines.append(f"| {task_id} | {title} | {category} | {confidence:.1%} | {dst} |")
        if len(tasks) > 20:
            lines.append(f"\n*... et {len(tasks) - 20} autres tâches*")
    else:
        lines.append("*Aucune tâche générée*")
    lines.append("")
    
    # Quality Scores
    lines.append("## Scores Qualité\n")
    lines.append(f"- **Extraction** : {quality_score.get('extraction_score', 0):.1%}")
    lines.append(f"- **Classification** : {quality_score.get('classification_score', 0):.1%}")
    lines.append(f"- **Génération tâches** : {quality_score.get('task_generation_score', 0):.1%}")
    lines.append(f"- **Preuves** : {quality_score.get('evidence_score', 0):.1%}")
    lines.append(f"- **Score global** : {quality_score.get('overall_score', 0):.1%} (**{quality_score.get('grade', 'F')}**)\n")
    
    # Footer
    lines.append("---")
    lines.append("\n*Rapport généré par BTP Engine Core*")
    
    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
