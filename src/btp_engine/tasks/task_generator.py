"""Generate tasks from document analysis."""

from typing import Dict, List
from .task_templates import TaskTemplates


class TaskGenerator:
    """Generate tasks based on document type and problems."""
    
    def __init__(self):
        self.templates = TaskTemplates()
        self.generated_tasks: List[Dict] = []
    
    def generate(self, doc_type: str, problems: List[Dict] = None) -> List[Dict]:
        """Generate tasks for document."""
        self.generated_tasks.clear()
        
        base_tasks = self.templates.get_templates(doc_type)
        for task in base_tasks:
            self.generated_tasks.append({
                "name": task["name"],
                "priority": task["priority"],
                "description": task["description"],
                "source": "template",
            })
        
        if problems:
            for problem in problems:
                if problem.get("severity") in ["critical", "high"]:
                    self.generated_tasks.append({
                        "name": f"Résoudre: {problem.get('description', 'problème')}",
                        "priority": "critical" if problem["severity"] == "critical" else "high",
                        "description": f"Action requise: {problem.get('description')}",
                        "source": "problem",
                        "problem_details": problem,
                    })
        
        return self.generated_tasks
    
    def get_critical_tasks(self) -> List[Dict]:
        """Get only critical priority tasks."""
        return [t for t in self.generated_tasks if t["priority"] == "critical"]
    
    def sort_by_priority(self) -> List[Dict]:
        """Sort tasks by priority."""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(
            self.generated_tasks,
            key=lambda t: priority_order.get(t["priority"], 99)
        )
