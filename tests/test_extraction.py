"""Test extraction module."""

import pytest
from btp_engine.extraction import TextCleaner


def test_text_cleaner_whitespace():
    """Test whitespace removal."""
    cleaner = TextCleaner()
    text = "Hello    world\n\n\n\nTest"
    cleaned = cleaner.remove_excessive_whitespace(text)
    assert "    " not in cleaned
    assert "\n\n\n" not in cleaned


def test_text_cleaner_page_numbers():
    """Test page number removal."""
    cleaner = TextCleaner()
    text = "Content\n5\nMore content"
    cleaned = cleaner.remove_page_numbers(text)
    assert "\n5\n" not in cleaned