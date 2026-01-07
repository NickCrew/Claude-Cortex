"""Skill activation logic based on keyword matching."""

import yaml
from pathlib import Path
from typing import List, Dict, Set


def load_activation_map(claude_dir: Path) -> Dict[str, List[str]]:
    """Load skill activation keywords from activation.yaml.

    Args:
        claude_dir: Path to the cortex directory

    Returns:
        Dictionary mapping skill names to their keyword lists

    Raises:
        FileNotFoundError: If activation.yaml doesn't exist
        yaml.YAMLError: If activation.yaml is malformed
    """
    activation_file = claude_dir / "skills" / "activation.yaml"

    if not activation_file.exists():
        raise FileNotFoundError(f"Activation file not found: {activation_file}")

    with open(activation_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "skills" not in data:
        return {}

    # Extract skill -> keywords mapping
    activation_map = {}
    for skill_name, config in data["skills"].items():
        if "keywords" in config:
            activation_map[skill_name] = [kw.lower() for kw in config["keywords"]]

    return activation_map


def analyze_text(text: str, claude_dir: Path) -> List[str]:
    """Analyze text and return matching skill names.

    Args:
        text: Input text to analyze for skill keywords
        claude_dir: Path to the cortex directory

    Returns:
        List of skill names that match keywords in the text
    """
    try:
        activation_map = load_activation_map(claude_dir)
    except (FileNotFoundError, yaml.YAMLError) as e:
        # Return empty list if activation map can't be loaded
        return []

    if not activation_map:
        return []

    # Normalize input text
    text_lower = text.lower()

    # Find matching skills
    matches: Set[str] = set()

    for skill_name, keywords in activation_map.items():
        for keyword in keywords:
            # Check if keyword appears in text
            # Use word boundary logic for better matching
            if keyword in text_lower:
                matches.add(skill_name)
                break  # Found match for this skill, move to next

    return sorted(matches)


def suggest_skills(text: str, claude_dir: Path) -> str:
    """Analyze text and format skill suggestions for CLI output.

    Args:
        text: Input text to analyze for skill keywords
        claude_dir: Path to the cortex directory

    Returns:
        Formatted string with skill suggestions
    """
    matching_skills = analyze_text(text, claude_dir)

    if not matching_skills:
        return "No matching skills found for the provided text."

    # Build formatted output
    lines = [f"Found {len(matching_skills)} matching skill(s):\n"]

    for skill in matching_skills:
        lines.append(f"  - {skill}")

    lines.append("\nTo view skill details, run: cortex skills info <skill-name>")

    return "\n".join(lines)
