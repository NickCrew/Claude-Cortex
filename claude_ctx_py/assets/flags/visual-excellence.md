# Visual Excellence Flags

Flags for UI/UX enhancement and visual polish across all platforms.

**Estimated tokens: ~250**

---

**--supersaiyan / --visual-excellence**
- Trigger: "make it beautiful", "polish", "eye candy", "visual excellence", UI/UX work
- Behavior: Universal visual excellence mode with auto-platform detection
- Core Philosophy:
  - Accessibility first (WCAG 2.1 AA minimum)
  - Performance always (smooth, fast, responsive)
  - Delight users (purposeful micro-interactions)
- Auto-Detection:
  - Analyzes project files (package.json, requirements.txt, Cargo.toml, etc.)
  - Detects frameworks (React, Textual, Click, Jekyll, etc.)
  - Loads platform-specific implementation automatically
- Platform Support:
  - **Web**: React, Vue, Svelte, vanilla JS → Framer Motion, Tailwind, animations
  - **TUI**: Textual, Ratatui, Bubbletea → Rich colors, smooth transitions, progress bars
  - **CLI**: Click, Typer, Cobra, Clap → Rich output, spinners, beautiful errors
  - **Docs**: Jekyll, Hugo, MkDocs → Typography, search, dark mode
  - **Native**: SwiftUI, Flutter, Jetpack → Platform-appropriate animations
- Manual Platform Override:
  - `--supersaiyan-web` - Force web implementation
  - `--supersaiyan-tui` - Force terminal UI
  - `--supersaiyan-cli` - Force CLI styling
  - `--supersaiyan-docs` - Force documentation
- Related: `@modes/Super_Saiyan.md` with platform-specific guides in `@modes/supersaiyan/`
- Commands: `/kamehameha` (Level 2), `/>9000` (Level 3)

**--kamehameha**
- Trigger: Manual `/kamehameha` command, "high impact effects", "particles"
- Behavior: Super Saiyan Level 2 - High-impact visual effects
- Platform Adaptations:
  - **Web**: Particle systems, explosions, 3D transforms, screen shake
  - **TUI**: Advanced animations, gradient effects, live updates
  - **CLI**: Streaming output, live tables, enhanced progress
  - **Docs**: Interactive diagrams, animated transitions
- Performance: Optimized for each platform while maintaining impact
- Related: Builds on `--supersaiyan`, precedes `--over9000`

**--over9000**
- Trigger: Manual `/>9000` or `/over9000`, "maximum power", "experimental"
- Behavior: Super Saiyan Level 3 - Reality-bending maximum effects
- Platform Adaptations:
  - **Web**: Full 3D (Three.js), physics, WebGL shaders, maximum effects
  - **TUI**: ASCII art effects, matrix rain, advanced visualizations
  - **CLI**: Advanced streaming, real-time graphs, parallel output
  - **Docs**: Cutting-edge features, interactive 3D diagrams
- Warning: Resource-intensive, use for demos/experiments/showcases
- Performance: Optimized per platform but pushes limits
- Related: Builds on `--kamehameha`, ultimate power level

**--a11y / --accessibility-first**
- Trigger: Public-facing UIs, government sites, e-commerce, inclusive design requirements
- Behavior: Enforce WCAG 2.1 AA (or AAA) accessibility standards throughout development
- Auto-enables: Accessibility auditing, screen reader testing, keyboard navigation validation
- Validates: Color contrast ratios (4.5:1 text, 3:1 UI), ARIA labels, semantic HTML, focus management
- Checks: Alt text for images, form labels, heading hierarchy, skip links, landmarks
- Reports: Accessibility violations with severity (critical, serious, moderate, minor) and remediation guidance
- Tests: Keyboard-only navigation, screen reader compatibility (NVDA, JAWS, VoiceOver), mobile accessibility
- Standards: WCAG 2.1 Level AA minimum, Section 508, ADA compliance, ARIA best practices
- Tools: axe-core, Lighthouse accessibility audit, Pa11y, WAVE, screen reader testing
- Related: Auto-enabled by `--supersaiyan` but can be used standalone for accessibility-focused work
- Ensures: Inclusive design, legal compliance, better UX for all users
