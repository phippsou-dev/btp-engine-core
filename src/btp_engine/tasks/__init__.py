"""Tasks module - Task generation and management."""

from .task_generator import generate_tasks
from .task_templates import get_task_template
from .task_merger import merge_similar_tasks

__all__ = ["generate_tasks", "get_task_template", "merge_similar_tasks"]
