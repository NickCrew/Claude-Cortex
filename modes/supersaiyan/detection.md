# Super Saiyan Platform Detection

**Purpose**: Auto-detect project type and load appropriate visual excellence implementation

## Detection Algorithm

### Phase 1: File System Analysis (Priority Order)

```python
# Check in this order:

1. Check for package.json (JavaScript/TypeScript)
   → Parse for frameworks: react, vue, svelte, next, nuxt
   → Result: Load @modes/supersaiyan/web.md

2. Check for requirements.txt or pyproject.toml (Python)
   → Search for: textual, rich, click, typer, flask, fastapi
   → If textual/rich → Load @modes/supersaiyan/tui.md
   → If click/typer → Load @modes/supersaiyan/cli.md
   → If flask/fastapi → Load @modes/supersaiyan/web.md

3. Check for Cargo.toml (Rust)
   → Search for: ratatui, tui-rs, crossterm, clap
   → If ratatui/tui-rs → Load @modes/supersaiyan/tui.md
   → If clap → Load @modes/supersaiyan/cli.md

4. Check for go.mod (Go)
   → Search for: bubbletea, cobra, termui
   → If bubbletea/termui → Load @modes/supersaiyan/tui.md
   → If cobra → Load @modes/supersaiyan/cli.md

5. Check for Gemfile (Ruby)
   → Search for: jekyll, middleman, rails
   → If jekyll/middleman → Load @modes/supersaiyan/docs.md
   → If rails → Load @modes/supersaiyan/web.md

6. Check for pubspec.yaml (Dart/Flutter)
   → Result: Load @modes/supersaiyan/native.md

7. Check for *.xcodeproj or *.swift (iOS/Mac)
   → Result: Load @modes/supersaiyan/native.md

8. Check for build.gradle or *.kt (Android/Kotlin)
   → Result: Load @modes/supersaiyan/native.md

9. Check for mkdocs.yml, conf.py, or _config.yml
   → Result: Load @modes/supersaiyan/docs.md

10. Check for index.html + CSS files only
    → Result: Load @modes/supersaiyan/web.md (vanilla)

11. No framework detected
    → Default: Ask user or use context clues
```

### Phase 2: Context Clues

If file detection is ambiguous, look for:

**User's request keywords:**
- "dashboard", "website", "webapp" → Web
- "terminal", "tui", "terminal ui" → TUI
- "command line", "cli tool" → CLI
- "documentation", "docs site" → Docs
- "iOS app", "Android app", "mobile" → Native

**File patterns:**
- `*.tsx`, `*.jsx` → React web
- `*.vue` → Vue web
- `*.svelte` → Svelte web
- `tui_*.py`, `*_tui.py` → Python TUI
- `cli_*.py`, `*_cli.py` → Python CLI
- `cmd/*.go` → Go CLI
- `*.md` in docs/ or documentation/ → Docs

### Phase 3: Multi-Platform Detection

Some projects have MULTIPLE UIs:

```python
Example: Python project with:
- Web API (FastAPI)
- CLI tool (Click)
- Documentation (MkDocs)

Detection result:
- Primary: @modes/supersaiyan/web.md (for API docs/dashboard)
- Secondary: @modes/supersaiyan/cli.md (for CLI)
- Tertiary: @modes/supersaiyan/docs.md (for docs site)

Action: Ask user which component to enhance
```

## Detection Decision Tree

```
START
│
├─ package.json exists?
│  ├─ YES → Check dependencies
│  │  ├─ react/next → WEB (React)
│  │  ├─ vue/nuxt → WEB (Vue)
│  │  ├─ svelte → WEB (Svelte)
│  │  ├─ angular → WEB (Angular)
│  │  └─ none → WEB (Vanilla)
│  └─ NO → Continue
│
├─ requirements.txt or pyproject.toml?
│  ├─ YES → Check dependencies
│  │  ├─ textual → TUI (Textual)
│  │  ├─ rich + click → CLI (Rich)
│  │  ├─ flask/fastapi → WEB (Python)
│  │  └─ none → Ask user
│  └─ NO → Continue
│
├─ Cargo.toml exists?
│  ├─ YES → Check dependencies
│  │  ├─ ratatui/tui-rs → TUI (Rust)
│  │  ├─ clap → CLI (Rust)
│  │  └─ none → Ask user
│  └─ NO → Continue
│
├─ go.mod exists?
│  ├─ YES → Check dependencies
│  │  ├─ bubbletea → TUI (Go)
│  │  ├─ cobra → CLI (Go)
│  │  └─ none → Ask user
│  └─ NO → Continue
│
├─ Gemfile exists?
│  ├─ YES → Check dependencies
│  │  ├─ jekyll → DOCS (Jekyll)
│  │  ├─ rails → WEB (Rails)
│  │  └─ none → Ask user
│  └─ NO → Continue
│
├─ mkdocs.yml or _config.yml?
│  ├─ YES → DOCS (Static site)
│  └─ NO → Continue
│
├─ *.swift or *.xcodeproj?
│  ├─ YES → NATIVE (iOS/Mac)
│  └─ NO → Continue
│
├─ *.kt or build.gradle?
│  ├─ YES → NATIVE (Android)
│  └─ NO → Continue
│
├─ pubspec.yaml?
│  ├─ YES → NATIVE (Flutter)
│  └─ NO → Continue
│
└─ Unable to detect
   → Ask user or default to context clues
```

## Implementation Examples

### Detector Function (Pseudocode)

```python
def detect_platform(project_root: Path) -> str:
    """Detect platform and return implementation path."""

    # Check package managers
    if (project_root / "package.json").exists():
        deps = parse_json(project_root / "package.json")
        if "react" in deps or "next" in deps:
            return "web"
        if "vue" in deps:
            return "web"
        # ... etc

    if (project_root / "requirements.txt").exists():
        deps = read_text(project_root / "requirements.txt")
        if "textual" in deps:
            return "tui"
        if "click" in deps or "typer" in deps:
            return "cli"
        if "fastapi" in deps or "flask" in deps:
            return "web"

    if (project_root / "Cargo.toml").exists():
        deps = parse_toml(project_root / "Cargo.toml")
        if "ratatui" in deps:
            return "tui"
        if "clap" in deps:
            return "cli"

    # Check for docs
    if (project_root / "mkdocs.yml").exists():
        return "docs"
    if (project_root / "_config.yml").exists():
        return "docs"

    # Check file patterns
    tsx_files = list(project_root.glob("**/*.tsx"))
    if tsx_files:
        return "web"

    # Default: ask user
    return ask_user_for_platform()

def load_supersaiyan_mode(platform: str):
    """Load platform-specific Super Saiyan implementation."""
    path = f"@modes/supersaiyan/{platform}.md"
    load_mode(path)
    print(f"🔥 Super Saiyan mode activated for {platform.upper()}!")
```

## User Prompts (When Detection Fails)

```markdown
Unable to auto-detect platform. What type of UI are you working on?

1. Web (React, Vue, HTML/CSS)
2. Terminal UI (Textual, Ratatui, Bubbletea)
3. CLI Tool (Click, Cobra, Clap)
4. Documentation Site (Jekyll, Hugo, MkDocs)
5. Native App (iOS, Android, Flutter)
6. Other (describe)

Enter number or platform name:
```

## Detection Confidence Scores

```python
confidence_scores = {
    "high": [
        "package.json with framework",
        "requirements.txt with TUI framework",
        "Cargo.toml with ratatui",
        "*.xcodeproj found",
    ],
    "medium": [
        "package.json without framework",
        "requirements.txt without obvious UI lib",
        "File patterns match (*.tsx, *.vue)",
    ],
    "low": [
        "No obvious indicators",
        "Multiple conflicting signals",
        "User context needed",
    ]
}
```

**Action by confidence:**
- **High**: Auto-load platform implementation
- **Medium**: Show detected platform, ask to confirm
- **Low**: Ask user to specify

## Override Flags

User can force specific platform:

```bash
--supersaiyan-web       # Force web implementation
--supersaiyan-tui       # Force TUI implementation
--supersaiyan-cli       # Force CLI implementation
--supersaiyan-docs      # Force docs implementation
--supersaiyan-native    # Force native implementation
```

## Multi-Platform Projects

For projects with multiple UIs:

```markdown
Detected multiple UI platforms:
- Web dashboard (FastAPI + React)
- CLI tool (Click)
- Documentation (MkDocs)

Which would you like to enhance?
1. All (apply appropriate mode to each)
2. Web dashboard only
3. CLI tool only
4. Documentation only

Enter number:
```

## Error Handling

```python
try:
    platform = detect_platform(cwd)
    load_supersaiyan_mode(platform)
except DetectionError:
    print("⚠️  Unable to detect platform")
    print("💡 Try: --supersaiyan-{web|tui|cli|docs|native}")
    print("Or describe your UI context in the request")
```

## Testing Detection

```bash
# Test detection on various projects
cortex supersaiyan detect ~/project1  # React app
cortex supersaiyan detect ~/project2  # Python TUI
cortex supersaiyan detect ~/project3  # Go CLI

# Output:
# Detected: WEB (React + Next.js)
# Confidence: HIGH
# Implementation: @modes/supersaiyan/web.md
```

## Detection Cache

To avoid repeated detection:

```python
# Cache detection result in .claude/cache/
cache_file = ".claude/cache/supersaiyan-platform.json"
{
  "project_root": "/path/to/project",
  "platform": "web",
  "confidence": "high",
  "detected_at": "2025-11-04T12:00:00Z",
  "frameworks": ["react", "next.js", "tailwind"]
}
```

**Cache invalidation:**
- User changes package.json
- User adds/removes framework
- User runs with `--supersaiyan-force-detect`

## Summary

Detection process:
1. **Scan** project files for platform indicators
2. **Analyze** dependencies and file patterns
3. **Score** confidence level
4. **Load** appropriate platform implementation
5. **Cache** result for future use

Result: The right Super Saiyan mode for your UI, automatically! 🎯🔥
