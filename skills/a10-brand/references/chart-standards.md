# A10 Chart Standards — Complete Reference

## Series Color Assignment

Always assign data series colors in this priority order:

| Priority | Name | HEX | Semantic |
|----------|------|-----|----------|
| 1 | A10 Blue | `#0057B7` | Primary series |
| 2 | Sky Blue | `#529EEC` | Secondary series |
| 3 | Green | `#00B140` | Success / positive |
| 4 | Orange | `#E35205` | Warning / caution |
| 5 | Red | `#EF3340` | Danger / error |
| 6 | Magenta | `#D62598` | Accent (if needed) |
| 7 | Cloud Blue | `#5E8AB4` | Additional series |
| 8 | Purple | `#440099` | Additional series |

For semantic data (success/failure, allowed/blocked), use the semantic mapping:
- Success/Allowed/Positive: Green or A10 Blue
- Warning/Caution: Orange
- Error/Blocked/Negative: Red
- Informational: Sky Blue or Cloud Blue

## Gradient Formula

Bars should use subtle gradients, never flat fills. This adds depth and polish.

**Vertical bars**: Lighten +30 at top → Darken -20 at bottom
```jsx
<linearGradient id="bar-v" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stopColor={lighten(baseColor, 30)} />
  <stop offset="100%" stopColor={darken(baseColor, 20)} />
</linearGradient>
```

**Horizontal bars**: Darken -20 at left → Lighten +30 at right
```jsx
<linearGradient id="bar-h" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stopColor={darken(baseColor, 20)} />
  <stop offset="100%" stopColor={lighten(baseColor, 30)} />
</linearGradient>
```

**Lighten/darken helper**:
```js
const lighten = (hex, amt) => {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.min(255, ((num >> 16) & 0xff) + amt);
  const g = Math.min(255, ((num >> 8) & 0xff) + amt);
  const b = Math.min(255, (num & 0xff) + amt);
  return `rgb(${r},${g},${b})`;
};
const darken = (hex, amt) => lighten(hex, -amt);
```

## Bar Styling

- **Highlight edge**: Left edge (vertical) or top edge (horizontal) with `rgba(255,255,255,0.12)`, 1.5-2px wide
- **Base opacity**: 0.9
- **Hover opacity**: 1.0
- **Transition**: `opacity 0.15s ease`
- **Corner radius**: 0 (never round bar corners)
- **Gap ratio**: ~0.3 between bars in a group

## Grid Lines

- **Style**: Dashed (`strokeDasharray="4,4"`)
- **Color**: Navy `#001E62` on dark backgrounds
- **Opacity**: 0.3 for grid lines, 0.8 for baseline (x-axis)
- **Baseline**: Solid, slightly more visible than grid

## Labels

- **Chart title**: Rubik Light 300, 20px, `#F0F4F8` (dark) or `#001E62` (light)
- **Subtitle**: Rubik Regular 400, 14px, `#7F7F7F` (Mid Gray), immediately below title
- **Axis labels**: Rubik Regular 400, 12px, `#7F7F7F`
- **Value labels**: Rubik Medium 500, 13px, `#F0F4F8` (dark) or `#001E62` (light)
- **Legend labels**: Rubik Regular 400, 12px, `#7F7F7F`
- **Legend markers**: 12x12px squares (not circles, not rounded), filled with series color

**Value formatting**:
- Values ≥ 1000: Format as `X.Xk` (e.g., `42.5k`)
- Values ≥ 10000: Format as `XXk` (e.g., `42k`) — drop decimal
- Always show value labels on bars (above for vertical, right of for horizontal)

## Chart Container

Dark theme (default for data viz):
```css
.chart-container {
  background: #0A1A3A;  /* Card Dark */
  padding: 24px;
  margin-bottom: 24px;
  /* No border-radius */
}
```

Light theme:
```css
.chart-container {
  background: #FFFFFF;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 30, 98, 0.1);
}
```

## Chart Types Available

Production-ready React components in `assets/chart-reference.jsx`:

1. **VerticalBarChart** — Single-series vertical bars with individual colors per bar
2. **HorizontalBarChart** — Single-series horizontal bars
3. **StackedHorizontalBar** — Multi-series stacked horizontal bars with legend
4. **GroupedVerticalBar** — Multi-series grouped vertical bars with legend

Each component accepts: `data`, `title`, `subtitle`, optional `height`, `showValues`, and
series-specific props. All follow the gradient, labeling, and interaction patterns above.

## Recharts Integration

When using the recharts library in React artifacts:

```jsx
const A10_CHART_COLORS = [
  '#0057B7', '#529EEC', '#00B140', '#E35205',
  '#EF3340', '#D62598', '#5E8AB4', '#440099'
];

// Apply to recharts
<BarChart>
  <CartesianGrid strokeDasharray="4 4" stroke="#001E62" opacity={0.3} />
  <XAxis tick={{ fill: '#7F7F7F', fontFamily: 'Rubik', fontSize: 12 }} />
  <YAxis tick={{ fill: '#7F7F7F', fontFamily: 'Rubik', fontSize: 12 }} />
  <Bar dataKey="value" fill="#0057B7" radius={0} /> {/* radius={0} critical */}
</BarChart>
```

## "Do / Don't" Summary

**Always**:
- Value labels on every data point
- Dashed grid lines (opacity 0.3)
- Rubik font (Light 300 titles, Regular 400 labels, Medium 500 values)
- Subtitle with temporal/contextual info
- Hover states with opacity change
- Gradient fills (not flat)
- Square legend markers

**Never**:
- Flat solid fills (use subtle gradient)
- Missing value labels
- Overlapping axis text
- Rounded corners on bars
- Colors outside brand palette
- 3D effects or shadows on data elements
- Pie charts with too many segments (max 6-8)
