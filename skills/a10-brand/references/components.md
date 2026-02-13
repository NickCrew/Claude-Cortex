# A10 Components — Complete Reference

## Buttons

### Critical: `border-radius: 0` on ALL buttons. No exceptions.

### Primary Button (Large) — A10 Blue

```css
.btn-primary {
  font-family: 'Rubik', sans-serif;
  font-weight: 500;
  font-size: 16px;
  height: 56px;
  padding: 0 32px;
  background-color: #0057B7;
  color: #FFFFFF;
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: background-color 0.15s ease;
}
.btn-primary:hover { background-color: #004189; }
```

### Primary Button — Magenta Variant

Use sparingly for the single most important CTA on a page.

```css
.btn-primary-magenta {
  font-family: 'Rubik', sans-serif;
  font-weight: 500;
  font-size: 16px;
  height: 56px;
  padding: 0 32px;
  background-color: #D62598;
  color: #FFFFFF;
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: background-color 0.15s ease;
}
.btn-primary-magenta:hover { background-color: #A01B72; }
```

### Outlined Button (Medium)

```css
.btn-outlined {
  font-family: 'Rubik', sans-serif;
  font-weight: 500;
  font-size: 14px;
  height: 48px;
  padding: 0 24px;
  background-color: transparent;
  color: #0057B7;
  border: 2px solid #0057B7;
  border-radius: 0;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-outlined:hover {
  background-color: #D62598;
  border-color: #D62598;
  color: #FFFFFF;
}
```

### Secondary Button (Small)

```css
.btn-secondary {
  font-family: 'Rubik', sans-serif;
  font-weight: 600;
  font-size: 12px;
  height: 40px;
  padding: 0 20px;
  background-color: #001E62;
  color: #FFFFFF;
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: background-color 0.15s ease;
}
.btn-secondary:hover { background-color: #00174A; }
```

### Dark Theme Buttons

```css
/* Primary - Dark */
.dark .btn-primary {
  background-color: #529EEC;
}
.dark .btn-primary:hover { background-color: #7CBAFF; }

/* Outlined - Dark */
.dark .btn-outlined {
  color: #F0F4F8;
  border-color: #F0F4F8;
}
.dark .btn-outlined:hover {
  background-color: #003EC8;
  border-color: #003EC8;
  color: #FFFFFF;
}
```

## Links

```css
.link {
  font-family: 'Rubik', sans-serif;
  font-weight: 600;
  font-size: 16px;
  color: #0057B7;
  text-decoration: none;
  transition: color 0.15s ease;
}
.link::after { content: ' >'; }
.link:hover { color: #003EC8; }

.dark .link { color: #529EEC; }
.dark .link:hover { color: #7CBAFF; }
```

## Cards

```css
.card {
  background: #FFFFFF;
  border: none;
  border-radius: 0;
  box-shadow: 0 2px 8px rgba(0, 30, 98, 0.1);
  padding: 24px;
}

.dark .card {
  background: #0A1A3A;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
```

Card variants from brand guide:
- **Dark Card**: Navy bg `#0A1A3A`, light text, for product/dashboard contexts
- **Light Card**: White bg, navy text, subtle shadow
- **Status Card**: Card with colored left border (3px) indicating status
- **Alert Card**: Card with colored top accent and icon

## Alert Styles

```css
.alert {
  padding: 16px 20px;
  border-radius: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Rubik', sans-serif;
  font-size: 14px;
}

.alert-success {
  background: rgba(0, 177, 64, 0.1);
  border-left: 3px solid #00B140;
  color: #001E62;
}
.alert-warning {
  background: rgba(227, 82, 5, 0.1);
  border-left: 3px solid #E35205;
  color: #001E62;
}
.alert-error {
  background: rgba(239, 51, 64, 0.1);
  border-left: 3px solid #EF3340;
  color: #001E62;
}
.alert-info {
  background: rgba(0, 87, 183, 0.1);
  border-left: 3px solid #0057B7;
  color: #001E62;
}
```

## Status Badges

```css
.badge {
  font-family: 'Rubik', sans-serif;
  font-weight: 500;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 0; /* Square badges */
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-success { background: #00B140; color: #FFFFFF; }
.badge-warning { background: #E35205; color: #FFFFFF; }
.badge-error   { background: #EF3340; color: #FFFFFF; }
.badge-info    { background: #0057B7; color: #FFFFFF; }
.badge-accent  { background: #D62598; color: #FFFFFF; }
.badge-new     { background: #529EEC; color: #FFFFFF; }
```

## Layout: Diagonal Split Hero

```css
.hero {
  position: relative;
  background: #001E62;
  min-height: 500px;
  overflow: hidden;
  padding: 80px 48px;
}

.hero-diagonal::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  background: #FFFFFF;
  clip-path: polygon(20% 0, 100% 0, 100% 100%, 0 100%);
}
```

## Layout: Section Alternation

Cycle through these backgrounds in order to create visual rhythm:

1. White `#FFFFFF`
2. Light Gray `#F0F4F8`
3. Navy `#001E62` (with white text)
4. A10 Blue `#0057B7` (with white text)

Use padding `48px 0` or `64px 0` for section spacing. No visible borders between sections —
the color change creates the separation.

## Layout: Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing, icon gaps |
| sm | 8px | Compact elements |
| md | 16px | Default component padding |
| lg | 24px | Card padding, section gaps |
| xl | 32px | Section padding, large gaps |
| 2xl | 48px | Section vertical padding |
| 3xl | 64px | Hero padding, major sections |

## Form Inputs

```css
input, select, textarea {
  font-family: 'Rubik', sans-serif;
  font-weight: 400;
  font-size: 16px;
  padding: 12px 16px;
  border: 2px solid #DFE8F0;
  border-radius: 0;
  background: #FFFFFF;
  color: #001E62;
  transition: border-color 0.15s ease;
}

input:focus, select:focus, textarea:focus {
  border-color: #0057B7;
  outline: none;
}

.dark input, .dark select, .dark textarea {
  background: #0A1A3A;
  border-color: #003EC8;
  color: #F0F4F8;
}
.dark input:focus { border-color: #529EEC; }
```

## Tables

```css
table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Rubik', sans-serif;
}

th {
  background: #001E62;
  color: #FFFFFF;
  font-weight: 500;
  font-size: 14px;
  padding: 12px 16px;
  text-align: left;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid #DFE8F0;
  font-size: 14px;
  color: #001E62;
}

tr:hover td { background: #F0F4F8; }

/* Dark theme */
.dark th { background: #00174A; }
.dark td {
  color: #F0F4F8;
  border-bottom-color: rgba(255, 255, 255, 0.08);
}
.dark tr:hover td { background: rgba(255, 255, 255, 0.04); }
```

## Global Resets

Apply to every A10 project:

```css
button, .btn, .card, input, select, textarea,
.badge, .alert, .tooltip, .modal, img.framed {
  border-radius: 0;
}
```
