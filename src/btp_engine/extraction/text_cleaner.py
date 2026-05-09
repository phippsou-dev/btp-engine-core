"""Text cleaning utilities."""

import re


def clean_text(text: str) -> str:
    """
    Clean extracted text.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove excessive newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_snippets(text: str, keywords: list, context_chars: int = 200) -> list:
    """
    Extract snippets around keywords.
    
    Args:
        text: Full text
        keywords: List of keywords to search for
        context_chars: Number of characters of context on each side
        
    Returns:
        List of snippets
    """
    snippets = []
    text_lower = text.lower()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        start = 0
        
        while True:
            pos = text_lower.find(keyword_lower, start)
            if pos == -1:
                break
            
            snippet_start = max(0, pos - context_chars)
            snippet_end = min(len(text), pos + len(keyword) + context_chars)
            
            snippet = text[snippet_start:snippet_end]
            snippets.append({
                "keyword": keyword,
                "position": pos,
                "snippet": snippet,
                "context_chars": context_chars
            })
            
            start = pos + 1
    
    return snippets
