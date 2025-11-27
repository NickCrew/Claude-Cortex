from typing import Dict, Tuple, List
from ..tui_icons import Icons

PROFILE_DESCRIPTIONS: Dict[str, str] = {
    "minimal": "Load minimal profile (essential agents only)",
    "frontend": "Load frontend profile (TypeScript + review)",
    "web-dev": "Load web-dev profile (full-stack)",
    "backend": "Load backend profile (Python + security)",
    "devops": "Load devops profile (infrastructure & deploy)",
    "documentation": "Load documentation profile (writing focus)",
    "data-ai": "Load data/AI profile",
    "quality": "Load quality profile (QA + security)",
    "meta": "Load meta tooling profile",
    "developer-experience": "Load DX profile",
    "product": "Load product development profile",
    "full": "Load full profile (all agents)",
}

EXPORT_CATEGORIES: List[Tuple[str, str, str]] = [
    ("core", "Core Framework", "FLAGS, PRINCIPLES, RULES"),
    ("rules", "Rules", "Active rule modules"),
    ("modes", "Modes", "Active behavioral modes"),
    ("agents", "Agents", "All available agents"),
    ("mcp_docs", "MCP Docs", "Model Context Protocol docs"),
    ("skills", "Skills", "Local skill definitions"),
]

DEFAULT_EXPORT_OPTIONS = {key: True for key, _label, _desc in EXPORT_CATEGORIES}

PRIMARY_VIEW_BINDINGS = [
    ("1", "overview", "Overview"),
    ("2", "agents", "Agents"),
    ("3", "modes", "Modes"),
    ("4", "rules", "Rules"),
    ("5", "skills", "Skills"),
    ("6", "workflows", "Workflows"),
    ("7", "mcp", "MCP"),
    ("8", "profiles", "Profiles"),
    ("9", "export", "Export"),
    ("0", "ai_assistant", "AI Assistant"),
]

VIEW_TITLES: Dict[str, str] = {
    "overview": f"{Icons.METRICS} Overview",
    "agents": f"{Icons.CODE} Agents",
    "modes": f"{Icons.FILTER} Modes",
    "rules": f"{Icons.DOC} Rules",
    "commands": f"{Icons.DOC} Slash Commands",
    "skills": f"{Icons.CODE} Skills",
    "workflows": f"{Icons.PLAY} Workflows",
    "scenarios": f"{Icons.PLAY} Scenarios",
    "orchestrate": "⚙ Orchestrate",
    "mcp": f"{Icons.METRICS} MCP Servers",
    "profiles": "👤 Profiles",
    "export": f"{Icons.FILE} Export",
    "ai_assistant": "🤖 AI Assistant",
    "tasks": f"{Icons.TEST} Tasks",
    "galaxy": "✦ Agent Galaxy",
}
