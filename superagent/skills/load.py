"""Skill loader for parsing and loading agent skills from SKILL.md files.

This module implements the "Agent Skills" pattern with progressive disclosure.
Each skill is a directory containing a SKILL.md file with:
- YAML frontmatter (name, description required)
- Markdown instructions for the agent
"""

import re
import contextlib
from pathlib import Path
from typing import TypedDict, List, Optional


class SkillMetadata(TypedDict):
    """Metadata for a skill."""
    name: str
    description: str
    path: str
    source: str  # 'user' or 'project'


def parse_skill_metadata(skill_md_path: Path, source: str) -> Optional[SkillMetadata]:
    """Parse YAML frontmatter from a SKILL.md file."""
    try:
        if not skill_md_path.exists():
            return None
            
        content = skill_md_path.read_text(encoding="utf-8").lstrip()
        
        # Match YAML frontmatter between --- delimiters
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if not match:
            return None
            
        frontmatter = match.group(1)
        metadata: dict[str, str] = {}
        
        for line in frontmatter.split("\n"):
            kv_match = re.match(r"^(\w+):\s*(.+)$", line.strip())
            if kv_match:
                key, value = kv_match.groups()
                metadata[key.strip()] = value.strip()
                
        if "name" not in metadata or "description" not in metadata:
            return None
            
        return SkillMetadata(
            name=metadata["name"],
            description=metadata["description"],
            path=str(skill_md_path.absolute()),
            source=source,
        )
    except (OSError, UnicodeDecodeError):
        return None


def list_skills(user_skills_dir: Optional[Path] = None, project_skills_dir: Optional[Path] = None) -> List[SkillMetadata]:
    """Scan and list skills from user and project directories."""
    all_skills: dict[str, SkillMetadata] = {}
    
    def scan_dir(directory: Path, source: str):
        if not directory.exists() or not directory.is_dir():
            return
        for skill_dir in directory.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                metadata = parse_skill_metadata(skill_md, source)
                if metadata:
                    all_skills[metadata["name"]] = metadata

    if user_skills_dir:
        scan_dir(user_skills_dir, "user")
        
    if project_skills_dir:
        # Project skills override user skills
        scan_dir(project_skills_dir, "project")
        
    return list(all_skills.values())
