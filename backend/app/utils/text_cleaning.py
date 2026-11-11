import re
import unicodedata
from typing import List


def clean_text(text: str) -> str:
    """Normalize unicode characters, whitespace, and remove stray control characters."""
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    # Replace non-standard bullets and dashes
    bullet_chars = ["•", "●", "○", "■", "▪", "▫", "◆", "◇", "➢", "", "–", "—"]
    for bc in bullet_chars[:10]:
        text = text.replace(bc, "\n- ")
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple spaces but preserve single newlines
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    cleaned = "\n".join(lines)
    # Collapse 3+ newlines into 2
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def escape_latex(text: str) -> str:
    """
    Escape special characters for LaTeX typesetting:
    & % $ # _ { } ~ ^ \\
    """
    if not text:
        return ""
    
    # Text replacements in safe order
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
        
    return text
