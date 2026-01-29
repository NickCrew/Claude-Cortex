# Super Saiyan: Docs Reference

Visual excellence for documentation sites using MkDocs, Hugo, Docusaurus.

## Stack
- Python: `mkdocs-material`
- Go: `hugo`
- React: `docusaurus`

## MkDocs Material Config
```yaml
theme:
  name: material
  palette:
    - scheme: default
      primary: blue
      accent: cyan
      toggle:
        icon: material/brightness-7
        name: Dark mode
    - scheme: slate
      primary: blue
      accent: cyan
      toggle:
        icon: material/brightness-4
        name: Light mode

  features:
    - navigation.instant
    - navigation.tabs
    - search.suggest
    - content.code.copy

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - admonition
  - toc:
      permalink: true
```

## Typography
```css
:root {
  --font-body: 'Inter', sans-serif;
  --font-code: 'JetBrains Mono', monospace;
  --text-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  --leading-relaxed: 1.625;
}
```

## Admonitions
```markdown
!!! note "Title"
    Content here

!!! tip "Pro Tip"
!!! warning "Caution"
!!! danger "Breaking Change"
```

## Checklist
- [ ] Clear homepage
- [ ] Quick start (<5 min)
- [ ] Searchable
- [ ] Syntax highlighting
- [ ] Copy code buttons
- [ ] Dark mode
- [ ] Mobile-friendly
- [ ] Load time <2s
