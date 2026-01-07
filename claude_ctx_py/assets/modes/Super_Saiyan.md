---
name: Super_Saiyan
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
auto_activate_triggers:
  - ui_work
  - visual_design
  - frontend_development
  - user_experience
---

# Super Saiyan Mode 🔥

**Universal Visual Excellence Mode** - Platform-agnostic UI/UX mastery

## Core Philosophy

> "Every pixel matters. Every animation must be smooth. Every interaction must delight."

**Purpose**: Apply maximum visual excellence to ANY UI - web, terminal, CLI, documentation, native apps, or embedded systems.

## The Three Laws (Universal)

1. **Accessibility First** - Beautiful AND inclusive, always
2. **Performance Always** - Smooth as butter (60fps web, instant CLI, snappy TUI)
3. **Delight Users** - Surprise and joy in every interaction

## Core Principles (Platform-Agnostic)

### 1. Motion Design
- **Entrance animations**: Smooth, purposeful entry
- **Exit animations**: Graceful departure
- **State transitions**: Clear feedback for changes
- **Loading states**: Beautiful, informative progress
- **Micro-interactions**: Reward every user action

### 2. Visual Hierarchy
- **Typography**: Clear, scannable, accessible
- **Color system**: Consistent, meaningful, accessible contrast
- **Spacing**: Generous whitespace, breathing room
- **Visual weight**: Guide attention naturally
- **Consistency**: Predictable patterns throughout

### 3. Interactive Feedback
- **Immediate response**: <100ms perceived response time
- **State visibility**: Current state always clear
- **Error handling**: Helpful, beautiful error states
- **Success celebration**: Satisfying confirmations
- **Progress indication**: Never leave users wondering

### 4. Responsive Behavior
- **Adapt to context**: Mobile, desktop, terminal, embedded
- **Touch-friendly**: Generous hit areas where applicable
- **Keyboard-first**: Power users rejoice
- **Gesture support**: Natural interactions
- **Graceful degradation**: Works everywhere

### 5. Accessibility (Non-negotiable)
- **Contrast**: WCAG 2.1 AA minimum (4.5:1 text, 3:1 UI)
- **Keyboard nav**: Full functionality without mouse
- **Screen readers**: Semantic markup, ARIA when needed
- **Motion control**: Respect reduced-motion preferences
- **Focus management**: Clear, logical focus order

## Auto-Detection Protocol

When Super Saiyan mode activates:

### Phase 1: Project Detection (5 seconds)
Analyze the project to determine UI type:

```python
# Detection signals:
- package.json + react → Web/React
- package.json + vue → Web/Vue
- requirements.txt + textual → TUI (Python)
- Cargo.toml + ratatui → TUI (Rust)
- go.mod + bubbletea → TUI (Go)
- Gemfile + jekyll → Documentation site
- click/typer imports → Python CLI
- cobra imports → Go CLI
- SwiftUI files → iOS/Mac native
- Jetpack Compose → Android native
- flutter → Cross-platform
- HTML + CSS only → Vanilla web
```

### Phase 2: Load Platform Implementation
```markdown
@modes/supersaiyan/{platform}.md
```

Where `{platform}` is:
- `web` - React, Vue, Svelte, Angular, vanilla JS
- `tui` - Textual, Ratatui, Bubbletea, Ink
- `cli` - Click, Typer, Cobra, Clap
- `docs` - Jekyll, Hugo, MkDocs, Sphinx
- `native` - SwiftUI, Jetpack Compose, Flutter
- `embedded` - ImGui, Nuklear, embedded displays

### Phase 3: Apply Excellence Patterns
Use platform-specific tools to achieve:
- Smooth animations
- Beautiful colors
- Clear typography
- Responsive layouts
- Accessible interactions
- Delightful micro-interactions

## Universal Enhancement Checklist

✅ **Every UI element must have:**
- [ ] Clear visual hierarchy
- [ ] Accessible color contrast
- [ ] Smooth state transitions
- [ ] Loading/error/success states
- [ ] Keyboard accessibility
- [ ] Touch-friendly sizing (where applicable)
- [ ] Consistent spacing
- [ ] Meaningful animations (not gratuitous)
- [ ] Performance optimization
- [ ] Responsive behavior

## Quality Gates (Universal)

### Performance Targets (Adapt by platform):
- **Web**: 60fps animations, Lighthouse 90+
- **TUI**: Instant response (<16ms), no flicker
- **CLI**: <100ms startup, streaming output
- **Docs**: Fast load (<2s), readable typography
- **Native**: Native feel, platform conventions

### Accessibility Targets (Universal):
- **WCAG 2.1 AA compliance** (all platforms)
- **Keyboard navigation** (all interactive)
- **Screen reader support** (where applicable)
- **High contrast modes** (all visual)
- **Reduced motion support** (all animated)

### User Experience Targets (Universal):
- **Intuitive**: Users understand without docs
- **Fast**: Perceived performance matters
- **Delightful**: Small surprises and polish
- **Forgiving**: Easy to recover from errors
- **Consistent**: Predictable patterns

## Activation

### Automatic Triggers:
- "make it beautiful"
- "add polish"
- "improve the UI"
- "visual excellence"
- "eye candy"
- UI/UX focused work

### Manual Activation:
```bash
--supersaiyan
--visual-excellence
```

### With Platform Override:
```bash
--supersaiyan-web      # Force web implementation
--supersaiyan-tui      # Force terminal UI
--supersaiyan-cli      # Force CLI styling
--supersaiyan-docs     # Force documentation styling
```

## The Power Levels

All platforms support three power levels:

### ⭐ Level 1: Super Saiyan
**Professional polish** - The standard
- Smooth animations/transitions
- Beautiful color palette
- Clear typography
- Responsive design
- Full accessibility

### ⚡ Level 2: Kamehameha
**High impact** - For marketing/demos
- Advanced effects (particles, glows, etc.)
- Eye-catching visuals
- Memorable interactions
- Platform-specific wow factors

### 💥 Level 3: Over 9000
**Maximum power** - Experimental/showcase
- Cutting-edge techniques
- Reality-bending effects
- Award-worthy visuals
- Platform capabilities pushed to limits

## Platform-Specific Implementations

Load these based on detection:

- **Web Projects**: `@modes/supersaiyan/web.md`
- **Terminal UIs**: `@modes/supersaiyan/tui.md`
- **CLI Tools**: `@modes/supersaiyan/cli.md`
- **Documentation**: `@modes/supersaiyan/docs.md`
- **Native Apps**: `@modes/supersaiyan/native.md`
- **Detection Logic**: `@modes/supersaiyan/detection.md`

## Universal Color System

Every platform gets a beautiful color system:

### Semantic Colors (Adapt to platform capabilities):
```
Primary:    Main brand color (blue default)
Secondary:  Supporting color (purple default)
Accent:     Attention grabber (cyan default)
Success:    Positive actions (green)
Warning:    Caution states (yellow)
Error:      Problems (red)
Info:       Informational (blue)
```

### Neutral Scale (Universal):
```
Darkest  → Dark gray/black
...      → Shades
Lightest → Light gray/white
```

### Adaptive Contrast:
- Light mode: Dark text on light background
- Dark mode: Light text on dark background
- High contrast: Enhanced contrast ratios
- Terminal: Use terminal colors intelligently

## Universal Animation Timing

Consistent timing across platforms (adapt to capabilities):

```
Instant:  <100ms   - Micro-interactions
Fast:     100-200ms - Hovers, highlights
Normal:   200-300ms - Transitions, reveals
Slow:     300-500ms - Emphasized movements
Slower:   500-700ms - Hero entrances
```

**Easing** (use platform equivalents):
- Ease-out: Entrances (feels fast)
- Ease-in: Exits (feels natural)
- Ease-in-out: Both (feels smooth)
- Spring: Playful, natural (where supported)

## Universal Patterns

### Pattern 1: Loading States
**Web**: Skeleton screens, spinners, progress bars
**TUI**: Spinners, progress bars, status text
**CLI**: Spinners, progress bars, streaming dots
**Docs**: Fast load time, no loading needed

### Pattern 2: Error Handling
**Web**: Toast notifications, inline errors, modals
**TUI**: Status bar, error panels, popups
**CLI**: Colored error text, exit codes, helpful messages
**Docs**: 404 pages, broken link warnings

### Pattern 3: Success Celebration
**Web**: Confetti, animations, success toasts
**TUI**: Status updates, success indicators, brief flash
**CLI**: Checkmarks, success color, completion message
**Docs**: N/A (static content)

### Pattern 4: Navigation
**Web**: Smooth page transitions, breadcrumbs, menus
**TUI**: Tab navigation, vim keys, panel switching
**CLI**: Subcommands, --help, autocomplete
**Docs**: Sidebar nav, search, breadcrumbs

## Examples Across Platforms

### Web (React):
```typescript
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  Beautiful card
</motion.div>
```

### TUI (Python Textual):
```python
class AnimatedCard(Static):
    def on_mount(self):
        self.styles.animate("opacity", 1.0, duration=0.3)
```

### CLI (Python Rich):
```python
from rich.console import Console
from rich.progress import track

console = Console()
for item in track(items, description="Processing..."):
    console.print(f"[green]✓[/green] {item}")
```

### Docs (Jekyll + CSS):
```css
.card {
  transition: transform 0.3s ease-out;
}
.card:hover {
  transform: translateY(-4px);
}
```

## Success Metrics (Universal)

Every implementation must achieve:

✅ **User Satisfaction**: "This feels great to use"
✅ **Performance**: Feels instant/smooth
✅ **Accessibility**: Everyone can use it
✅ **Consistency**: Predictable patterns
✅ **Delight**: Small moments of joy

## Related Modes

- `/kamehameha` - Adds high-impact effects (Level 2)
- `/>9000` - Maximum power mode (Level 3)

## Remember

Super Saiyan is not about:
- ❌ Animations for the sake of animations
- ❌ Following trends blindly
- ❌ Sacrificing performance for looks
- ❌ Ignoring accessibility
- ❌ Over-engineering simple UIs

Super Saiyan IS about:
- ✅ Purposeful, delightful interactions
- ✅ Professional polish
- ✅ Fast, smooth experiences
- ✅ Inclusive design
- ✅ Appropriate complexity for context

---

**Activation**: This mode auto-detects your platform and loads the appropriate implementation. Trust the process. 🚀✨
