"""Test tasks module."""

import pytest
from btp_engine.tasks import TaskGenerator, TaskMerger


def test_task_generator():
    """Test task generation."""
    generator = TaskGenerator()
    tasks = generator.generate("facture")
    assert len(tasks) > 0
    assert all("name" in t for t in tasks)


def test_task_generator_with_problems():
    """Test task generation with problems."""
    generator = TaskGenerator()
    problems = [{"severity": "critical", "description": "Test problem"}]
    tasks = generator.generate("facture", problems)
    critical_tasks = generator.get_critical_tasks()
    assert len(critical_tasks) > 0


def test_task_merger():
    """Test task merging."""
    tasks = [
        {"name": "Task 1", "priority": "high"},
        {"name": "Task 1", "priority": "medium"},
        {"name": "Task 2", "priority": "low"},
    ]
    merged = TaskMerger.merge_duplicate_tasks(tasks)
    assert len(merged) == 2