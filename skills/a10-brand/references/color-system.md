# A10 Color System — Complete Reference

## Primary Colors

| Name | HEX | RGB | Pantone | Usage |
|------|-----|-----|---------|-------|
| **A10 Blue** | `#0057B7` | 0, 87, 183 | 2935 C | Primary brand, CTAs, links |
| **Navy Blue** | `#001E62` | 0, 30, 98 | 2758 C | Dark backgrounds, headers, primary text |
| **White** | `#FFFFFF` | 255, 255, 255 | — | Light backgrounds, text on dark |

## Secondary Colors

| Name | HEX | RGB | Pantone | Usage |
|------|-----|-----|---------|-------|
| **Sky Blue** | `#529EEC` | 82, 158, 236 | 292 C | Dark theme links, accents |
| **Magenta** | `#D62598` | 214, 37, 152 | Pink C | **Accent only** — badges, highlights, buttons |
| **Black** | `#000000` | 0, 0, 0 | Black | Dark backgrounds, body text |

## Accent Colors (Data & Status Only)

| Name | HEX | RGB | Usage |
|------|-----|-----|-------|
| **Purple** | `#440099` | 68, 0, 153 | Charts, illustrations |
| **Orange** | `#E35205` | 227, 82, 5 | Warnings, emphasis |
| **Cloud Blue** | `#5E8AB4` | 94, 138, 180 | Charts, alternative to gray |
| **Green** | `#00B140` | 0, 177, 64 | Success states |
| **Red** | `#EF3340` | 239, 51, 64 | Error states |

## Tints & Shades

| Base | Light Tint | Medium | Dark Shade | Darker |
|------|------------|--------|------------|--------|
| A10 Blue `#0057B7` | `#F0F4F8` | `#7CBAFF` | `#004189` | `#00174A` |
| Navy `#001E62` | `#DFE8F0` | `#003EC8` | `#00174A` | — |
| Sky Blue `#529EEC` | `#BEDDFF` | — | `#3D77B1` | — |
| Magenta `#D62598` | `#E979C2` | — | `#A01B72` | — |

## UI Neutrals

| Name | HEX | Usage |
|------|-----|-------|
| Light Gray | `#F0F4F8` | Section backgrounds (light theme) |
| Medium Gray | `#DFE8F0` | Cards, subtle backgrounds, gridlines |
| Dark Gray | `#404040` | Secondary text (light theme) |
| Mid Gray | `#7F7F7F` | Muted text, disabled states |
| Card Dark | `#0A1A3A` | Dark theme cards |

## Hover States

| Context | Default | Hover |
|---------|---------|-------|
| Blue button (light) | `#0057B7` | `#004189` |
| Blue button (dark) | `#529EEC` | `#7CBAFF` |
| Magenta button | `#D62598` | `#A01B72` |
| Navy button | `#001E62` | `#00174A` |
| Link (light) | `#0057B7` | `#003EC8` |
| Link (dark) | `#529EEC` | `#7CBAFF` |
| Outlined button hover fill (light) | transparent | `#DFE8F0` |
| Outlined button hover fill (dark) | transparent | `#003EC8` |

## Gradients (Approved)

| Name | Gradient | Usage |
|------|----------|-------|
| Navy → Blue | `135deg: #001E62 0% → #0057B7 100%` | Hero backgrounds |
| Magenta → Dark | `135deg: #D62598 0% → #A01B72 100%` | Accent CTAs |
| Blue Scale (3-stop) | `90deg: #0057B7 0% → #529EEC 50% → #7CBAFF 100%` | Progress bars, accent strips |
| Purple → Magenta | `135deg: #440099 0% → #D62598 100%` | Special feature highlights |

## Contrast Rules

- **White text safe on**: `#001E62`, `#000000`, `#00174A`, `#0A1A3A`, `#0057B7`, `#D62598`, `#440099`
- **Dark text safe on**: `#FFFFFF`, `#F0F4F8`, `#DFE8F0`, `#BEDDFF`, `#7CBAFF`
- **Magenta**: Accent only — never dominant, never behind body text
- **Logo**: Never on accent color backgrounds
- **Minimum contrast**: WCAG 2.1 AA — 4.5:1 for normal text, 3:1 for large text (≥24px or ≥18.66px bold)

## Usage Proportions

Visual weight targets across any A10-branded surface:

| Tier | Colors | Target | Role |
|------|--------|--------|------|
| Primary | Navy, A10 Blue, White | ~80% | Structure, backgrounds, text |
| Secondary | Sky Blue, Magenta, Black | ~15% | Accents, secondary interactions |
| Accent | Purple, Cloud Blue, Orange, Green, Red | ~5% | Data viz, status, KPIs |

Magenta specifically should be ≤8% of total color presence. If magenta is the first thing you
notice on every screen, reduce it.

## CSS Custom Properties

```css
:root {
  /* Primary */
  --a10-blue: #0057B7;
  --a10-navy: #001E62;
  --a10-white: #FFFFFF;

  /* Secondary */
  --a10-sky-blue: #529EEC;
  --a10-magenta: #D62598;
  --a10-black: #000000;

  /* Accent */
  --a10-purple: #440099;
  --a10-orange: #E35205;
  --a10-cloud-blue: #5E8AB4;
  --a10-green: #00B140;
  --a10-red: #EF3340;

  /* Neutrals */
  --a10-gray-light: #F0F4F8;
  --a10-gray-medium: #DFE8F0;
  --a10-gray-dark: #404040;
  --a10-gray-mid: #7F7F7F;
  --a10-card-dark: #0A1A3A;

  /* Tints & Shades */
  --a10-blue-light: #7CBAFF;
  --a10-blue-dark: #004189;
  --a10-blue-darker: #00174A;
  --a10-sky-light: #BEDDFF;
  --a10-sky-dark: #3D77B1;
  --a10-magenta-light: #E979C2;
  --a10-magenta-dark: #A01B72;

  /* Hover */
  --a10-hover-light: #003EC8;
  --a10-hover-dark: #7CBAFF;
}
```
