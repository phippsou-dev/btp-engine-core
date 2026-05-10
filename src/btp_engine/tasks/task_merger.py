"""Merge and deduplicate tasks."""

from typing import List, Dict


class TaskMerger:
    """Merge and deduplicate similar tasks."""
    
    @staticmethod
    def merge_duplicate_tasks(tasks: List[Dict]) -> List[Dict]:
        """Merge tasks with identical names."""
        seen = {}
        merged = []
        
        for task in tasks:
            name = task.get("name", "")
            if name in seen:
                existing = seen[name]
                if task.get("priority") == "critical":
                    existing["priority"] = "critical"
            else:
                seen[name] = task
                merged.append(task)
        
        return merged
    
    @staticmethod
    def merge_similar_tasks(tasks: List[Dict], similarity_threshold: float = 0.8) -> List[Dict]:
        """Merge tasks with similar names (simple version)."""
        return TaskMerger.merge_duplicate_tasks(tasks)