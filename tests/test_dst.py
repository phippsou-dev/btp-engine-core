"""Test DST module."""

import pytest
from btp_engine.dst import DSTMapper, DSTRules


def test_dst_rules():
    """Test DST rules."""
    rules = DSTRules()
    structure = rules.get_structure("facture")
    assert "required_sections" in structure
    assert len(structure["required_sections"]) > 0


def test_dst_mapper():
    """Test DST mapping."""
    mapper = DSTMapper()
    text = "header items totals footer"
    result = mapper.map_document(text, "facture")
    assert "sections" in result
    assert "completeness" in result
    assert result["completeness"] > 0