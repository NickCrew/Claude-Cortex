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
    ("1", "overview", "Overview"),
    ("2", "agents", "Agents"),
    ("3", "rules", "Rules"),
    ("4", "skills", "Skills"),
    ("C", "worktrees", "Worktrees"),
    ("5", "tasks", "Tasks"),
    ("6", "commands", "Commands"),
    ("E", "export", "Export"),
    ("0", "ai_assistant", "AI Assistant"),
    ("w", "watch_mode", "Watch Mode"),
    ("A", "assets", "Assets"),
    ("M", "memory", "Memory"),
    ("X", "codex_skills", "Codex Skills"),
]

VIEW_TITLES: Dict[str, str] = {
    "overview": f"{Icons.METRICS} Overview",
    "agents": f"{Icons.CODE} Agents",
    "rules": f"{Icons.DOC} Rules",
    "commands": f"{Icons.DOC} Slash Commands",
    "skills": f"{Icons.CODE} Skills",
    "worktrees": f"{Icons.FOLDER} Worktrees",
    "export": f"{Icons.FILE} Export",
    "ai_assistant": "🤖 AI Assistant",
    "watch_mode": "🔍 Watch Mode",
    "tasks": f"{Icons.TEST} Tasks",
    "assets": "📦 Asset Manager",
    "memory": "🧠 Memory Vault",
    "codex_skills": "🔗 Codex Skills",
}
