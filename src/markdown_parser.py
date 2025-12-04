"""Markdown parser utilities for extracting README sections."""

import re
from src.config import (
    MARKDOWN_SECTIONS,
    INSTALL_PATTERNS,
    USAGE_PATTERNS,
    PREREQ_PATTERNS,
    FEATURE_PATTERNS,
)


def extract_markdown_sections(markdown_content: str) -> dict[str, str]:
    """Extract key sections from markdown README."""
    sections = MARKDOWN_SECTIONS.copy()
    
    if not markdown_content:
        return sections
    
    # Parse markdown to get structure
    lines = markdown_content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        # Check if it's a header
        if line.startswith('#'):
            # Save previous section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Determine new section
            header_text = line.lower()
            current_content = []
            
            if any(re.search(p, header_text) for p in INSTALL_PATTERNS):
                current_section = "installation"
            elif any(re.search(p, header_text) for p in USAGE_PATTERNS):
                current_section = "usage"
            elif any(re.search(p, header_text) for p in PREREQ_PATTERNS):
                current_section = "prerequisites"
            elif any(re.search(p, header_text) for p in FEATURE_PATTERNS):
                current_section = "features"
            else:
                current_section = None
        elif current_section:
            current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # Consolidate quickstart/getting_started
    if sections["usage"] and len(sections["usage"]) < 1000:
        sections["quickstart"] = sections["usage"]
    
    return sections


def extract_code_blocks(text: str) -> list[str]:
    """Extract code blocks from markdown text."""
    code_blocks = re.findall(r'```[\w]*\n(.*?)```', text, re.DOTALL)
    return [block.strip() for block in code_blocks if block.strip()]
