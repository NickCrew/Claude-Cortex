---
layout: default
title: Overview
nav_order: 1
permalink: /
---

# Claude CTX Plugin – Documentation Hub

> Version 1.1.0 · Last updated November 15, 2025

<div class="hero">
  <div class="hero__copy">
    <h2>Your single source of truth for Claude CTX.</h2>
    <p>
      Every setup guide, workflow tutorial, and CLI reference now lives under two simple buckets:
      <strong>Guides</strong> and <strong>Reference</strong>. Jump directly to what you need and skip the archival clutter.
    </p>
    <div class="hero__cta">
      <a href="{{ '/guides/' | relative_url }}" class="primary">Browse Guides →</a>
      <a href="{{ '/reference/' | relative_url }}" class="secondary">Open Reference →</a>
    </div>
    <div class="hero__pills">
      <span>Guides</span>
      <span>Reference</span>
      <span>CLI &amp; TUI</span>
      <span>MCP Ready</span>
    </div>
  </div>
  <div class="hero__visual">
    <img src="{{ '/assets/images/hero.png' | relative_url }}" alt="Claude CTX blueprint" />
  </div>
</div>

## Quick Links

<div class="quick-links">
  <a href="{{ '/guides/' | relative_url }}">Guides Directory</a>
  <a href="{{ '/reference/' | relative_url }}">Reference Library</a>
  <a href="{{ '/guides/getting-started.html' | relative_url }}">Install &amp; Setup</a>
  <a href="{{ '/guides/tui.html' | relative_url }}">TUI Tour</a>
  <a href="{{ '/guides/commands.html' | relative_url }}">Command Reference</a>
  <a href="{{ '/reference/architecture/architecture-diagrams.html' | relative_url }}">Architecture</a>
</div>

---

## Start Here

<div class="doc-grid">
  <a class="doc-card" href="{{ '/guides/getting-started.html' | relative_url }}">
    <h3>Getting Started</h3>
    <p>Install claude-ctx, configure completions, and verify the CLI.</p>
    <span class="doc-card__meta">Setup · 10 min</span>
  </a>
  <a class="doc-card" href="{{ '/guides/commands.html' | relative_url }}">
    <h3>Command Reference</h3>
    <p>Understand every slash command, argument, and flag.</p>
    <span class="doc-card__meta">CLI · Reference</span>
  </a>
  <a class="doc-card" href="{{ '/guides/tui.html' | relative_url }}">
    <h3>TUI Guide</h3>
    <p>Walk through the Rich/Textual dashboard, shortcuts, and palette.</p>
    <span class="doc-card__meta">TUI · Visual</span>
  </a>
  <a class="doc-card" href="{{ '/guides/agents.html' | relative_url }}">
    <h3>Agents Playbook</h3>
    <p>Profiles, behaviors, and orchestration techniques for agents.</p>
    <span class="doc-card__meta">AI · Workflows</span>
  </a>
</div>

## Guides Directory

All written guidance—TUI walkthroughs, MCP integration notes, skills documentation, scenario recipes—now surfaces in the <a href="{{ '/guides/' | relative_url }}">Guides directory</a>. Use browser search on that page or rely on the auto-generated cards. Highlights include:

- **Workflow & skills** – `guides/skills.md`, `guides/features/` deep dives, progressive disclosure strategies.
- **Integrations** – `guides/mcp/`, `guides/hooks.md`, and `guides/completions.md` for shell support.
- **TUI power user content** – command palette, layout tours, and quick-start flows.

Each file is rendered directly from the repository, so updates land on GitHub Pages within the next deploy.

## Reference Library

Need canonical specs instead of tutorials? Head to the <a href="{{ '/reference/' | relative_url }}">Reference landing page</a> for:

- **Architecture notes** – diagram packs, quick-reference briefs, and system overviews inside `reference/architecture/`.
- **Man pages** – downloadable `claude-ctx.1`, `claude-ctx-tui.1`, and `claude-ctx-workflow.1` for local `man` usage.
- **Supplemental artifacts** – exported documentation, CLI help snapshots, and any future spec sheets.

## Build & Preview Locally

Serve the site with:

```bash
just docs
# or: cd docs && bundle exec jekyll serve --livereload
```

The `.jekyllignore` configuration drops archival folders (`archive/`, `designs/`, `features/`, `presentations/`, and `TEST*.md`) so the published site stays focused on Guides and Reference material only.
