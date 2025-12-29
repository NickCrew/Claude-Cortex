# Claude Cortex Presentations

Reveal.js presentation decks for claude-ctx project overview, demos, and enablement sessions.

## 📊 Available Presentations

### 🤖 Claude Cortex Overview

**File:** `claude-ctx-overview.html`
**Topics:** Platform overview, AI intelligence, watch mode, metrics, architecture, testing

**What's Covered:**

- AI Intelligence System (context detection, pattern learning)
- Watch Mode (real-time monitoring, auto-activation)
- Metrics & Analytics (ROI, effectiveness scoring)
- Architecture Overview (modules, storage, CLI)
- Developer Workflow (tech stack, testing, coverage)
- Super Saiyan Mode (universal visual excellence)
- Recent achievements and roadmap

**Screenshots:** Includes TUI screenshots for overview, AI intelligence, and agent management

### 🎨 TUI Dashboard Showcase

**File:** `tui-showcase.html`
**Topics:** Interactive TUI walkthrough with screenshots of all views

**What's Covered:**

- Dashboard Overview (unified stats and quick actions)
- AI Assistant (press 0 - review requests + real-time recommendations)
- Agent Management (press 1 - dependency tracking)
- Slash Commands (press 2 - command reference)
- Rules Management (press 5 - rule modules)
- Workflows (press 7 - workflow orchestration)
- Orchestration (press 6 - multi-agent coordination)
- Keyboard Navigation (shortcuts and quick actions)
- TUI Features (real-time updates, mouse support, responsive design)

**Screenshots:** Full-screen TUI captures for every major view

## 🚀 Viewing Presentations

### Local Development Server

**Option 1: Python HTTP Server**

```bash
cd presentations
python3 -m http.server 8080

# Then open in browser:
open http://localhost:8080/claude-ctx-overview.html
open http://localhost:8080/tui-showcase.html
```

**Option 2: Node.js HTTP Server**

```bash
cd presentations
npx http-server -p 8080

# Then open in browser:
open http://localhost:8080/claude-ctx-overview.html
open http://localhost:8080/tui-showcase.html
```

### Direct File Opening

```bash
open presentations/claude-ctx-overview.html
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

1. **Project Overview** - Introduce claude-ctx to team members
2. **Demo Preparation** - Review features before customer demos
3. **Enablement Sessions** - Onboard new developers
4. **Architecture Review** - Explain system design decisions
5. **Progress Updates** - Show testing and coverage improvements

## 📝 Creating New Presentations

To create a new presentation following the same style:

1. Copy `claude-ctx-overview.html` as a template
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
http://localhost:8080/claude-ctx-overview.html?print-pdf
```

---

**Questions?** See the main README or check the Reveal.js documentation.
