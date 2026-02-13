# A10 Typography — Complete Reference

## Font Family

**Primary**: Rubik (Google Font)
```html
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

**Office fallback**: Calibri
**System fallback**: `-apple-system, BlinkMacSystemFont, sans-serif`

**Full stack**: `'Rubik', 'Calibri', -apple-system, BlinkMacSystemFont, sans-serif`

## Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Light | 300 | H1, H2, H3, H4 — all large headlines |
| Regular | 400 | Body copy, paragraphs, subheads, chart labels |
| Medium | 500 | H5, H6, buttons, navigation, labels |
| SemiBold | 600 | Links, small buttons, emphasis |
| Bold | 700 | Eyebrows only (ALL-CAPS labels), sparingly |

The most common mistake is using Bold for headlines. A10 headlines use Light 300 — this creates
the brand's distinctive elegant, modern feel. Bold is reserved almost exclusively for small
uppercase eyebrow labels.

## Type Scale

| Element | Size (px) | Size (rem) | Line Height | Weight | Additional |
|---------|-----------|------------|-------------|--------|------------|
| Eyebrow | 16px | 1rem | 1.2 | Bold 700 | ALL-CAPS, letter-spacing: 0.1em |
| H1 | 48px | 3rem | 56px | Light 300 | |
| H2 | 32px | 2rem | 40px | Light 300 | |
| H3 | 28px | 1.75rem | 36px | Light 300 | |
| H4 | 24px | 1.5rem | 32px | Light 300 | |
| H5 | 20px | 1.25rem | 28px | Medium 500 | |
| H6 | 16px | 1rem | 24px | Medium 500 | |
| Subhead | 20px | 1.25rem | 28px | Regular 400 | |
| Body | 16px | 1rem | 24px | Regular 400 | |
| Small | 14px | 0.875rem | 20px | Regular 400 | |

## Typography Rules

- **Alignment**: Ragged-right (left-aligned). Never justified text.
- **Kerning**: Optical kerning enabled (`font-kerning: normal; text-rendering: optimizeLegibility;`)
- **Hyphenation**: Never. (`hyphens: none;`)
- **ALL-CAPS**: Only for eyebrows and small labels. Never for body text or headlines.
- **Quotes**: Smart quotes (" ") for dialogue; straight quotes (") for measurements/code.
- **Brand names**: Keep "A10 Networks" and product names on the same line (`white-space: nowrap`).
- **Line length**: Aim for 60-80 characters per line for body text readability.

## CSS Implementation

```css
/* Base typography */
body {
  font-family: 'Rubik', 'Calibri', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 1.5;
  font-kerning: normal;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  hyphens: none;
}

/* Headlines — Light 300 */
h1 { font-size: 3rem; line-height: 56px; font-weight: 300; }
h2 { font-size: 2rem; line-height: 40px; font-weight: 300; }
h3 { font-size: 1.75rem; line-height: 36px; font-weight: 300; }
h4 { font-size: 1.5rem; line-height: 32px; font-weight: 300; }

/* Sub-headlines — Medium 500 */
h5 { font-size: 1.25rem; line-height: 28px; font-weight: 500; }
h6 { font-size: 1rem; line-height: 24px; font-weight: 500; }

/* Eyebrow */
.eyebrow {
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  line-height: 1.2;
}

/* Links */
a {
  font-weight: 600;
  text-decoration: none;
}
```

## Office / Print Context

When Rubik is unavailable (PowerPoint, Word, print):
- Use **Calibri** as the primary font
- Maintain the same weight relationships (Light for headlines, Regular for body)
- Print minimum: 10pt body, 8pt captions
- Ensure 300 DPI for print output
