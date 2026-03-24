from typing import Dict, Tuple, List
from ..tui_icons import Icons

EXPORT_CATEGORIES: List[Tuple[str, str, str]] = [
    ("core", "Core Framework", "RULES"),
    ("rules", "Rules", "Active rule modules"),
    ("agents", "Agents", "All available agents"),
    ("skills", "Skills", "Local skill definitions"),
]

DEFAULT_EXPORT_OPTIONS = {key: True for key, _label, _desc in EXPORT_CATEGORIES}

PRIMARY_VIEW_BINDINGS = [
    ("0", "ai_assistant", "AI Assistant"),
    ("1", "overview", "Overview"),
    ("2", "agents", "Agents"),
    ("3", "rules", "Rules"),
    ("4", "skills", "Skills"),
    ("5", "codex_skills", "LLM Skills"),
    ("6", "commands", "Commands"),
    ("7", "hooks", "Hooks"),
    ("8", "memory", "Memory"),
    ("9", "watch_mode", "Watch Mode"),
    ("M", "mcp", "MCP"),
    ("E", "export", "Export"),
    ("T", "tasks", "Tasks"),
    ("W", "worktrees", "Worktrees"),
    ("A", "assets", "Assets"),
    ("F", "settings", "Settings"),
]

VIEW_TITLES: Dict[str, str] = {
    "overview": f"{Icons.METRICS} Overview",
    "agents": f"{Icons.CODE} Agents",
    "rules": f"{Icons.DOC} Rules",
    "commands": f"{Icons.DOC} Slash Commands",
    "skills": f"{Icons.CODE} Skills",
    "worktrees": f"{Icons.FOLDER} Worktrees",
    "mcp": "🔌 MCP Servers",
    "export": f"{Icons.FILE} Export",
    "ai_assistant": "🤖 AI Assistant",
    "watch_mode": "🔍 Watch Mode",
    "tasks": f"{Icons.TEST} Tasks",
    "assets": "📦 Asset Browser",
    "memory": "🧠 Memory Vault",
    "hooks": "🪝 Hooks",
    "codex_skills": "🔗 LLM Skills",
    "settings": "⚙️  Settings",
}
