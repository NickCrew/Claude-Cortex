---
name: SUPER_SAIYAN_UNIVERSAL
category: visual
priority: medium
conflicts:
  - Minimal_UI
  - Token_Efficient
group: visual_style
tags:
  - ui
  - ux
  - accessibility
  - visual
  - design
  - animation
  - universal
auto_activate_triggers:
  - ui_work
  - visual_design
  - frontend_development
  - user_experience
---

# Super Saiyan Mode: Universal Edition 🔥🌍

**The Platform-Agnostic Visual Excellence Framework**

## What Is This?

Super Saiyan mode is a **universal** visual excellence system that automatically detects your project type and applies platform-appropriate polish, animations, and user experience enhancements.

> **One mode, every platform. From web apps to terminal UIs to CLI tools to documentation sites.**

## The Three Laws (Universal)

1. **Accessibility First** - Beautiful AND inclusive, always (WCAG 2.1 AA)
2. **Performance Always** - Smooth as butter (60fps web, instant CLI, snappy TUI)
3. **Delight Users** - Surprise and joy in every interaction

## How It Works

### Step 1: Auto-Detection

When you activate Super Saiyan mode, it scans your project:

```python
package.json + react      → WEB (React)
requirements.txt + textual → TUI (Python Textual)
Cargo.toml + clap         → CLI (Rust)
_config.yml + jekyll      → DOCS (Jekyll)
pubspec.yaml + flutter    → NATIVE (Flutter)
```

**Detection happens in ~5 seconds** and is cached for future use.

### Step 2: Platform-Specific Implementation

Based on detection, loads the appropriate implementation:

| Platform | Implementation File | Tech Stack |
|----------|-------------------|------------|
| **Web** | `@modes/supersaiyan/web.md` | Framer Motion, Tailwind, Shadcn/ui |
| **TUI** | `@modes/supersaiyan/tui.md` | Textual, Rich, colored output |
| **CLI** | `@modes/supersaiyan/cli.md` | Click/Typer, Rich, progress bars |
| **Docs** | `@modes/supersaiyan/docs.md` | Typography, search, dark mode |
| **Native** | `@modes/supersaiyan/native.md` | SwiftUI, Jetpack, platform patterns |

### Step 3: Apply Excellence Patterns

Each platform gets:
- ✨ Smooth animations (appropriate for platform)
- 🎨 Beautiful colors (terminal-safe for TUI, true color for web)
- 📊 Clear typography (web fonts or terminal-safe)
- ♿ Full accessibility (WCAG AA compliant)
- ⚡ Optimized performance (60fps web, instant CLI)
- 🎯 Platform conventions (native feel)

## The Three Power Levels

### ⭐ Level 1: Super Saiyan (Base)
**For:** Production apps, daily use
**What:** Professional polish, smooth UX
**Activation:** Automatic on keywords or `--supersaiyan`

**Web:**
- Framer Motion animations
- Tailwind styling
- Shadcn/ui components
- Lighthouse 90+

**TUI:**
- Rich colors and borders
- Smooth transitions
- Progress bars
- Status indicators

**CLI:**
- Colored output
- Spinners
- Beautiful errors
- Help text

### ⚡ Level 2: Kamehameha (Impact)
**For:** Marketing sites, demos, portfolios
**What:** High-impact effects
**Activation:** `/kamehameha` command

**Web:**
- Particle systems
- Explosions on success
- 3D transforms
- Screen shake

**TUI:**
- Gradient effects
- Live updating tables
- Advanced animations
- Sparklines

**CLI:**
- Streaming output
- Live tables
- Real-time progress
- Enhanced feedback

### 💥 Level 3: Over 9000 (Maximum)
**For:** Experimental, showcases, awards
**What:** Reality-bending effects
**Activation:** `/>9000` command

**Web:**
- Full 3D (Three.js)
- Physics simulation
- WebGL shaders
- Gesture controls

**TUI:**
- ASCII art effects
- Matrix rain
- Advanced graphs
- Terminal 3D

**CLI:**
- Parallel streaming
- Real-time charts
- Advanced visualizations
- Interactive graphs

## Activation Examples

### Automatic (Context-Aware)

```
User: "Make this dashboard beautiful"
→ Detects: React app
→ Loads: @modes/supersaiyan/web.md
→ Applies: Framer Motion animations, Tailwind polish
```

```
User: "Polish my terminal UI"
→ Detects: Textual (Python)
→ Loads: @modes/supersaiyan/tui.md
→ Applies: Rich colors, smooth transitions
```

```
User: "Improve my CLI tool's output"
→ Detects: Click (Python)
→ Loads: @modes/supersaiyan/cli.md
→ Applies: Rich output, progress bars
```

### Manual (Flag-Based)

```bash
--supersaiyan              # Auto-detect and apply
--supersaiyan-web          # Force web implementation
--supersaiyan-tui          # Force TUI implementation
--supersaiyan-cli          # Force CLI implementation
--supersaiyan-docs         # Force docs implementation

/kamehameha                # Level 2 (high impact)
/>9000                     # Level 3 (maximum power)
```

## Quick Reference

### Trigger Keywords

**Super Saiyan activates when you say:**
- "make it beautiful"
- "polish the UI"
- "add eye candy"
- "visual excellence"
- "improve UX"
- "make it shine"

**Platform override:**
- "for web" → Force web
- "for terminal" → Force TUI
- "for CLI" → Force CLI

### What Gets Enhanced

**Web Projects:**
- ✅ Components with animations
- ✅ Hover effects (lift, glow, scale)
- ✅ Loading states (skeleton screens)
- ✅ Success/error states
- ✅ Responsive layouts
- ✅ Dark mode support

**TUI Projects:**
- ✅ Rich color schemes
- ✅ Animated panels
- ✅ Beautiful tables
- ✅ Progress indicators
- ✅ Status updates
- ✅ Keyboard shortcuts

**CLI Projects:**
- ✅ Colored output
- ✅ Progress bars
- ✅ Spinners
- ✅ Beautiful errors
- ✅ Structured output
- ✅ Help text

**Documentation:**
- ✅ Typography scale
- ✅ Search functionality
- ✅ Code highlighting
- ✅ Dark mode
- ✅ Navigation
- ✅ Responsive design

## File Structure

```
~/.claude/
├── modes/
│   ├── Super_Saiyan.md              # Core generic mode
│   └── supersaiyan/
│       ├── detection.md             # Auto-detection logic
│       ├── web.md                   # Web implementation
│       ├── tui.md                   # Terminal UI implementation
│       ├── cli.md                   # CLI implementation
│       ├── docs.md                  # Documentation sites
│       └── native.md                # Native apps (iOS, Android, Flutter)
├── commands/
│   ├── kamehameha.md               # Level 2 command
│   └── over9000.md                 # Level 3 command
└── FLAGS.md                         # Flag definitions
```

## Detection Confidence

| Confidence | Action | Example |
|------------|--------|---------|
| **HIGH** | Auto-load | package.json with "react" |
| **MEDIUM** | Confirm with user | package.json without framework |
| **LOW** | Ask user | No obvious indicators |

**Override anytime** with platform flags.

## Platform Support Matrix

| Platform | Status | Power Levels | Examples |
|----------|--------|--------------|----------|
| **Web (React)** | ✅ Full | 1, 2, 3 | Dashboards, marketing sites |
| **Web (Vue)** | ✅ Full | 1, 2, 3 | SPAs, admin panels |
| **Web (Svelte)** | ✅ Full | 1, 2, 3 | Fast web apps |
| **TUI (Textual)** | ✅ Full | 1, 2, 3 | Python terminal apps |
| **TUI (Ratatui)** | ✅ Full | 1, 2, 3 | Rust terminal apps |
| **TUI (Bubbletea)** | ✅ Full | 1, 2, 3 | Go terminal apps |
| **CLI (Click)** | ✅ Full | 1, 2 | Python CLI tools |
| **CLI (Typer)** | ✅ Full | 1, 2 | Python CLI tools |
| **CLI (Cobra)** | ✅ Full | 1, 2 | Go CLI tools |
| **CLI (Clap)** | ✅ Full | 1, 2 | Rust CLI tools |
| **Docs (Jekyll)** | ✅ Full | 1 | Ruby static sites |
| **Docs (Hugo)** | ✅ Full | 1 | Go static sites |
| **Docs (MkDocs)** | ✅ Full | 1 | Python docs |
| **Native (SwiftUI)** | 🚧 Beta | 1 | iOS/Mac apps |
| **Native (Flutter)** | 🚧 Beta | 1 | Cross-platform |
| **Native (Jetpack)** | 🚧 Beta | 1 | Android apps |

## Real-World Examples

### Example 1: Python TUI (Textual)

**Before:**
```python
# Plain text UI
print("Status: Active")
print("Progress: 75%")
```

**After Super Saiyan:**
```python
# Rich, colorful UI
console.print("[green]✓[/green] Status: [bold cyan]Active[/bold cyan]")
progress = Progress()
task = progress.add_task("[cyan]Processing...", total=100)
progress.update(task, advance=75)
```

### Example 2: Python CLI (Click)

**Before:**
```python
# Plain output
print("Deploying...")
print("Done")
```

**After Super Saiyan:**
```python
# Beautiful output
with console.status("[cyan]Deploying..."):
    deploy()
console.print("[green]✓[/green] Deployment successful!")
```

### Example 3: React Web App

**Before:**
```jsx
// Static card
<div className="card">
  <h3>Stats</h3>
  <p>100</p>
</div>
```

**After Super Saiyan:**
```jsx
// Animated card
<motion.div
  className="card"
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  whileHover={{ y: -4 }}
>
  <h3>Stats</h3>
  <CountUp end={100} duration={2} />
</motion.div>
```

## Performance Impact

| Platform | Bundle Size | Load Time | Runtime |
|----------|-------------|-----------|---------|
| **Web** | +65-720KB | +0.2-1.0s | 60fps |
| **TUI** | +0KB* | 0s | Instant |
| **CLI** | +0KB* | 0s | <100ms |
| **Docs** | +10-50KB | +0.1s | Static |

*Python/Rust dependencies, not bundle size

## Testing Your Implementation

```bash
# Test detection
Say: "What platform is this?" (should auto-detect)

# Test enhancement
Say: "Make it beautiful" (should apply appropriate mode)

# Test override
Say: "--supersaiyan-tui please" (should force TUI mode)

# Test levels
Say: "/kamehameha" (should activate Level 2)
Say: "/ >9000" (should activate Level 3)
```

## Troubleshooting

### "Wrong platform detected"
**Solution:** Use override flag: `--supersaiyan-{web|tui|cli|docs}`

### "No visual changes"
**Solution:** Check if platform implementation exists in `~/.claude/modes/supersaiyan/`

### "Too slow"
**Solution:** Drop to Level 1 or disable: `--no-supersaiyan`

### "Accessibility concerns"
**Solution:** All modes respect `prefers-reduced-motion` and WCAG standards

## Summary

Super Saiyan mode is:
- **🌍 Universal**: Works on any UI platform
- **🧠 Smart**: Auto-detects your project type
- **⚡ Fast**: Optimized for each platform
- **♿ Accessible**: WCAG AA compliant always
- **🎯 Flexible**: Three power levels for different needs
- **🔧 Override-able**: Manual platform selection available

**One mode. Every platform. Always beautiful.** 🔥✨

---

## Quick Start

1. **Say:** "Make this beautiful"
2. **Claude:** *Detects platform and applies Super Saiyan mode*
3. **Result:** Your UI gets platform-appropriate polish automatically

That's it! 🚀
