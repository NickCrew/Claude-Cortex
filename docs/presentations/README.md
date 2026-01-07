# Cortex Presentations

Reveal.js presentation decks for cortex project overview, demos, and enablement sessions.

## 📊 Available Presentations

### 🚀 Cortex Intro Overview

**File:** `cortex-overview.html`
**Topics:** High-level platform overview, AI intelligence, watch mode, asset manager, visual excellence

**What's Covered:**

- AI Intelligence System (context detection, pattern learning)
- Watch Mode (real-time monitoring, auto-activation)
- Asset Manager + setup guardrails
- Super Saiyan Mode (visual excellence system)
- Multi-LLM consult skill + provider settings
- Recent improvements and momentum

**Screenshots:** Agent galaxy, AI assistant, watch mode, asset manager, command palette

### 🧠 Technical Deep Dive

**File:** `cortex-technical-deep-dive.html`
**Topics:** Activation pipeline, intelligence signals, watch mode, skill ratings, plugin + CLI integration

**What's Covered:**

- Activation + recommendation pipeline
- Signal sources and confidence scoring
- Watch mode loop and tuning
- Skill ratings + feedback loop
- Plugin and CLI integration + install flow
- Operational controls for activation

**Screenshots:** Galaxy, AI assistant, watch mode, flags, CLI usage

### 📈 Executive Overview & Roadmap

**File:** `cortex-executive-roadmap.html`
**Topics:** Business value, capability highlights, adoption plan, and roadmap

**What's Covered:**

- Value proposition and operating leverage
- Capability highlights (watch mode, visual excellence, asset manager)
- Recent improvements and readiness
- Phased roadmap and adoption plan
- Risks and mitigations

**Screenshots:** AI assistant hero shot

### 🎨 Feature Catalog (TUI + CLI)

**File:** `tui-showcase.html`
**Topics:** Comprehensive feature catalog with how-to guidance and docs links

**What's Covered:**

- Agent Galaxy (Press g)
- AI Assistant (Press 0)
- AI Watch Mode (Press w)
- Agents (Press 2)
- Skills (Press 5)
- Command Palette (Ctrl+P)
- Slash Commands (Press /)
- Modes (Press 3)
- Profiles (Press 8)
- Principles (Press p)
- Flags Explorer (Press F)
- Workflows (Press 6)
- Scenarios (Press S)
- Worktrees (Press C)
- Asset Manager (Press A)
- Hooks Manager (Press h)
- Backup Manager (Press b)
- Memory Vault (Press M)
- MCP Manager (Press 7)
- Export (Press 9)
- Setup Wizard (Press I)
- Shortcuts & Help (Press ?)
- CLI Usage (Terminal)

**Screenshots:** Full-screen TUI captures with feature descriptions and docs links

## 🚀 Viewing Presentations

### Local Development Server

**Option 1: Python HTTP Server**

```bash
cd presentations
python3 -m http.server 8080

# Then open in browser:
open http://localhost:8080/cortex-overview.html
open http://localhost:8080/cortex-technical-deep-dive.html
open http://localhost:8080/cortex-executive-roadmap.html
open http://localhost:8080/tui-showcase.html
```

**Option 2: Node.js HTTP Server**

```bash
cd presentations
npx http-server -p 8080

# Then open in browser:
open http://localhost:8080/cortex-overview.html
open http://localhost:8080/cortex-technical-deep-dive.html
open http://localhost:8080/cortex-executive-roadmap.html
open http://localhost:8080/tui-showcase.html
```

### Direct File Opening

```bash
open presentations/cortex-overview.html
open presentations/cortex-technical-deep-dive.html
open presentations/cortex-executive-roadmap.html
open presentations/tui-showcase.html
```

Note: Some features may require a local server due to CORS restrictions.

## 🎨 Presentation Style

**Theme:** Dark mode with blue/magenta gradient
**Font:** Rubik (Google Fonts)
**Framework:** Reveal.js 5
**Features:**

- Smooth fade transitions
- Animated gradients and glows
- Hover effects on cards and badges
- Glass morphism design
- Responsive grid layouts

## ⌨️ Keyboard Controls

**Navigation:**

- `→` / `Space` - Next slide
- `←` - Previous slide
- `Home` - First slide
- `End` - Last slide
- `Esc` - Slide overview

**Presentation:**

- `F` - Fullscreen
- `S` - Speaker notes (if available)
- `B` / `.` - Pause/blackout
- `?` - Help overlay

## 🎯 Use Cases

1. **Project Overview** - Intro deck for team onboarding
2. **Technical Deep Dive** - Activation, intelligence, watch mode, and ratings
3. **Executive Briefings** - Roadmap and adoption planning
4. **Feature Catalog** - Full capability walkthrough with docs links
5. **Demo Preparation** - Review features before customer demos
6. **Enablement Sessions** - Onboard new developers
7. **Progress Updates** - Highlight recent improvements

## 📝 Creating New Presentations

To create a new presentation following the same style:

1. Copy `cortex-overview.html` as a template
2. Update the `<title>` and metadata
3. Modify slide content within `<section>` tags
4. Adjust `data-background` gradients for visual variety
5. Use existing CSS classes for consistency:
   - `.feature-card` - Feature highlights
   - `.callout` - Important information boxes
   - `.two-col` / `.three-col` - Grid layouts
   - `.badge` - Technology/feature badges
   - `.mono` - Code/command formatting

## 🎨 Color Palette

```css
--primary-blue: #0256B6    /* Main brand blue */
--deep-navy: #001E62       /* Dark navy */
--sky-blue: #519DEC        /* Bright sky blue */
--magenta: #D62597         /* Accent magenta */
--purple: #430098          /* Deep purple */
--success-green: #02B040   /* Success states */
--alert-orange: #E35205    /* Warnings */
```

## 📦 Dependencies

**CDN Resources:**

- **Reveal.js 5:** Core presentation framework
- **Google Fonts:** Rubik font family
- **Fira Code:** Monospace code font (system fallback)

No build step required - presentations work standalone.

## 🔧 Customization

### Background Variations

```html
<!-- Cool blue gradient -->
<section data-background="radial-gradient(circle at center, rgba(81, 157, 236, 0.3) 0%, rgba(2, 5, 16, 0.95) 60%)">

<!-- Warm magenta gradient -->
<section data-background="radial-gradient(circle at top left, rgba(214, 37, 151, 0.25) 0%, rgba(2, 5, 16, 0.95) 60%)">

<!-- Success green gradient -->
<section data-background="radial-gradient(circle at bottom right, rgba(2, 176, 64, 0.2) 0%, rgba(2, 5, 16, 0.95) 60%)">
```

### Grid Layouts

```html
<!-- Two columns -->
<div class="two-col">
  <div>Left content</div>
  <div>Right content</div>
</div>

<!-- Three columns -->
<div class="three-col">
  <div class="feature-card">Card 1</div>
  <div class="feature-card">Card 2</div>
  <div class="feature-card">Card 3</div>
</div>
```

### Feature Cards

```html
<div class="feature-card">
  <h3>Card Title</h3>
  <p>Card description with <strong>highlighted text</strong></p>
  <p>Use <span class="mono">code formatting</span> for commands</p>
</div>
```

## 📚 Resources

- **Reveal.js Docs:** <https://revealjs.com/>
- **Google Fonts:** <https://fonts.google.com/specimen/Rubik>
- **Project README:** ../README.md
- **AI Intelligence Guide:** ../guides/development/AI_INTELLIGENCE_GUIDE.md
- **Watch Mode Guide:** ../guides/development/WATCH_MODE_GUIDE.md

## 🎭 Presentation Tips

1. **Use speaker notes** - Add `<aside class="notes">` for presenter context
2. **Practice timing** - Aim for 2-3 minutes per slide
3. **Test locally first** - Verify all animations and images work
4. **Prepare for questions** - Have documentation links ready
5. **Use overview mode** - Press `Esc` to see slide grid

## 🔄 Updates

When updating presentations:

1. Update slide content in HTML
2. Test in browser (both Chrome and Firefox)
3. Verify all links and images work
4. Update this README if adding new presentations
5. Consider exporting to PDF for distribution

## 📤 Exporting

**To PDF:**

1. Open presentation in Chrome
2. Add `?print-pdf` to URL
3. Use Print → Save as PDF
4. Ensure "Background graphics" is enabled

**Example:**

```
http://localhost:8080/cortex-overview.html?print-pdf
```

---

**Questions?** See the main README or check the Reveal.js documentation.
