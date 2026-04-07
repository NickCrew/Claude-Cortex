---
name: chart-builder
description: "Use this skill when creating data visualizations, selecting the right chart type, or generating chart code. Trigger phrases: 'build a chart', 'visualize this data', 'create a graph', 'plot these numbers', 'which chart should I use for'. Not for building interactive dashboards, designing UI components, or creating infographics with design tools like Figma."
version: 1.0.0
author: community
tags: [data, visualization, charts, graphs]
license: MIT
---

# Chart Builder

## Overview
This skill provides a systematic approach to data visualization—from choosing the right chart type for your data and message, to implementing it in Python (matplotlib/seaborn) or JavaScript (Chart.js). It covers chart anatomy, color principles, accessibility requirements, and common pitfalls, so every chart communicates its insight clearly and honestly.

## When to Use
- You need to communicate a data insight visually
- You're unsure which chart type fits your data shape and message
- You need reproducible chart code in Python or JavaScript
- You want to improve a chart that isn't communicating clearly
- You're building a report, slide deck, or embedded visualization

## When NOT to Use
- Building a full interactive BI dashboard (use dashboard-designer skill)
- Designing data art or infographics for marketing
- Creating maps or geospatial visualizations (use a GIS tool)
- Animating data for video production

## Quick Reference
| Chart Type | Best For | Avoid When |
|------------|----------|------------|
| Bar (vertical) | Comparing categories, rankings | Too many categories (>12) |
| Bar (horizontal) | Long category labels, rankings | Showing trends over time |
| Line | Trends over time, continuous data | Categorical/unordered x-axis |
| Scatter | Correlation between two variables | Fewer than ~20 data points |
| Pie / Donut | Part-of-whole (max 5 slices) | Comparing many segments |
| Heatmap | Matrix of values, correlation tables | Audiences unfamiliar with the format |
| Box plot | Distribution comparison across groups | Presenting to non-technical audience |
| Histogram | Distribution of a single variable | Showing trends or comparisons |
| Area | Cumulative totals over time | Multiple overlapping series |
| Stacked bar | Part-of-whole across categories | Comparing absolute values |

## Instructions

### Step 1: Choose the Right Chart Type
Answer these questions:
1. **How many variables?** 1 (distribution) → histogram/box. 2 (relationship) → scatter/line. 2+ (comparison) → bar/heatmap.
2. **What's the x-axis?** Time → line/area. Categories → bar. Continuous numeric → scatter.
3. **What's the message?** Trend → line. Ranking → bar. Proportion → pie (≤5 slices). Correlation → scatter.

### Step 2: Chart Anatomy — Label Everything
A complete chart has:
- **Title**: one-sentence insight, not just the topic ("West Region Revenue Up 34% in Q3", not "Revenue by Region")
- **Axis labels** with units (e.g., "Revenue (USD thousands)")
- **Legend** (if multiple series)
- **Data source** in a footer note
- **Gridlines**: horizontal only, light grey, behind data

### Step 3: Color Principles
- Use **2–4 colors maximum** for categorical data
- Use a **sequential palette** (light→dark) for ordered/quantitative data
- Use **diverging palette** (blue→white→red) for data with a meaningful midpoint (e.g., % change, NPS)
- **Never use red/green alone**—colorblind users cannot distinguish them; add pattern or shape
- Highlight the most important series in a strong color; grey out everything else

### Step 4: Accessibility Checklist
- Minimum contrast ratio 4.5:1 for text against background
- Add alt text describing the chart's key finding
- Don't rely on color alone to encode information (add labels, patterns)
- Font size minimum 12pt for axis labels, 14pt for titles
- Provide a data table below the chart for screen readers

### Step 5: Python Implementation (matplotlib / seaborn)

**Bar chart:**
```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

df = pd.DataFrame({
    'Region': ['West', 'East', 'North', 'South'],
    'Revenue': [4200, 3100, 1800, 2700]
})

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(df['Region'], df['Revenue'], color=['#2563EB', '#64748B', '#64748B', '#64748B'])
ax.set_title("West Region Leads Q3 Revenue", fontsize=16, fontweight='bold', pad=12)
ax.set_xlabel("Region", fontsize=12)
ax.set_ylabel("Revenue (USD thousands)", fontsize=12)
ax.yaxis.grid(True, color='#E5E7EB', linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[['top', 'right']].set_visible(False)

# Value labels on bars
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
            f"${bar.get_height():,.0f}K", ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig("revenue_by_region.png", dpi=150, bbox_inches='tight')
plt.show()
```

**Line chart (trend):**
```python
import matplotlib.pyplot as plt
import pandas as pd

df = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Revenue': [180, 210, 195, 240, 285, 310]
})

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(df['Month'], df['Revenue'], color='#2563EB', linewidth=2.5, marker='o', markersize=7)
ax.fill_between(range(len(df)), df['Revenue'], alpha=0.08, color='#2563EB')
ax.set_title("Revenue Growing Steadily — Up 72% H1", fontsize=16, fontweight='bold')
ax.set_ylabel("Revenue (USD thousands)", fontsize=12)
ax.yaxis.grid(True, color='#E5E7EB', linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig("revenue_trend.png", dpi=150, bbox_inches='tight')
```

**Scatter plot (correlation):**
```python
import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 6))
sns.regplot(data=df, x='marketing_spend', y='revenue', ax=ax,
            scatter_kws={'alpha': 0.6, 'color': '#2563EB'},
            line_kws={'color': '#DC2626', 'linewidth': 1.5})
ax.set_title("Marketing Spend Strongly Correlates with Revenue (r=0.78)", fontsize=14, fontweight='bold')
ax.set_xlabel("Marketing Spend (USD)", fontsize=12)
ax.set_ylabel("Revenue (USD)", fontsize=12)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
```

**Heatmap (correlation matrix):**
```python
import seaborn as sns
import matplotlib.pyplot as plt

corr = df[['revenue', 'units_sold', 'discount_pct', 'marketing_spend']].corr()
fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, square=True, linewidths=0.5, ax=ax)
ax.set_title("Correlation Matrix — Sales Variables", fontsize=14, fontweight='bold')
plt.tight_layout()
```

### Step 6: JavaScript Implementation (Chart.js)

**Bar chart:**
```html
<canvas id="revenueChart" width="600" height="400"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('revenueChart').getContext('2d');
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['West', 'East', 'North', 'South'],
    datasets: [{
      label: 'Revenue (USD K)',
      data: [4200, 3100, 1800, 2700],
      backgroundColor: ['#2563EB', '#64748B', '#64748B', '#64748B'],
      borderRadius: 4,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: { display: true, text: 'West Region Leads Q3 Revenue', font: { size: 16 } },
      legend: { display: false }
    },
    scales: {
      y: { grid: { color: '#E5E7EB' }, ticks: { callback: v => `$${v}K` } },
      x: { grid: { display: false } }
    }
  }
});
</script>
```

**Line chart (multi-series):**
```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Revenue',
        data: [180, 210, 195, 240, 285, 310],
        borderColor: '#2563EB',
        backgroundColor: 'rgba(37,99,235,0.08)',
        fill: true,
        tension: 0.3,
        pointRadius: 5
      },
      {
        label: 'Target',
        data: [200, 220, 220, 250, 270, 300],
        borderColor: '#DC2626',
        borderDash: [6, 3],
        fill: false,
        pointRadius: 0
      }
    ]
  },
  options: {
    plugins: { title: { display: true, text: 'Revenue vs Target — H1 2024' } },
    scales: { y: { grid: { color: '#E5E7EB' } } }
  }
});
```

## Examples

### Example 1: Build a Sales Trend Line Chart
**Input:** "I have monthly revenue data for 2023 and want to show the growth trend."

**Step 1 — Chart choice:** Time series data → **line chart**. Message is trend → line with a subtle fill works well.

**Step 2 — Python code:**
```python
import matplotlib.pyplot as plt
import pandas as pd

data = {
    'month': pd.date_range('2023-01', periods=12, freq='MS'),
    'revenue': [210, 195, 230, 255, 280, 310, 295, 340, 365, 390, 410, 445]
}
df = pd.DataFrame(data)
mom_growth = (df['revenue'].iloc[-1] / df['revenue'].iloc[0] - 1) * 100

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['month'], df['revenue'], color='#2563EB', linewidth=2.5, marker='o', markersize=6)
ax.fill_between(df['month'], df['revenue'], alpha=0.07, color='#2563EB')
ax.set_title(f"Revenue Up {mom_growth:.0f}% in 2023", fontsize=16, fontweight='bold')
ax.set_ylabel("Revenue (USD thousands)", fontsize=12)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b'))
ax.yaxis.grid(True, color='#E5E7EB', linewidth=0.8, linestyle='--')
ax.set_axisbelow(True)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig("2023_revenue_trend.png", dpi=150, bbox_inches='tight')
```

**Output:** A clean line chart titled "Revenue Up 112% in 2023" with subtle area fill, gridlines only on y-axis, no top/right spines.

---

### Example 2: Build a Comparison Bar Chart
**Input:** "Compare Q3 revenue across 5 product categories, highlighting which ones are above target."

**Step 1 — Chart choice:** Comparing categories → **horizontal bar chart** (better for 5 labels). Highlight above-target bars differently.

**Step 2 — Python code:**
```python
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'Category': ['Analytics', 'Storage', 'Compute', 'Networking', 'Security'],
    'Revenue':   [4200, 2800, 3600, 1500, 3100],
    'Target':    [3800, 3000, 3500, 2000, 2900]
})
df['above_target'] = df['Revenue'] >= df['Target']
colors = ['#2563EB' if above else '#94A3B8' for above in df['above_target']]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(df['Category'], df['Revenue'], color=colors, height=0.6)
ax.vlines(df['Target'], -0.4, len(df)-0.6, colors='#DC2626', linewidth=1.5,
          linestyle='--', label='Target')

ax.set_title("3 of 5 Categories Beat Q3 Revenue Target", fontsize=15, fontweight='bold')
ax.set_xlabel("Revenue (USD thousands)", fontsize=12)
ax.xaxis.grid(True, color='#E5E7EB', linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[['top', 'right']].set_visible(False)

# Labels
for bar, val in zip(bars, df['Revenue']):
    ax.text(val + 30, bar.get_y() + bar.get_height()/2,
            f"${val:,}K", va='center', fontsize=10)

from matplotlib.patches import Patch
legend_elements = [Patch(color='#2563EB', label='Above Target'),
                   Patch(color='#94A3B8', label='Below Target')]
ax.legend(handles=legend_elements, loc='lower right')
plt.tight_layout()
plt.savefig("category_vs_target.png", dpi=150, bbox_inches='tight')
```

**Output:** Horizontal bar chart with blue bars (above target) and grey bars (below target), red dashed target line, value labels on each bar.

## Best Practices
- Title the chart with the insight, not just the topic (e.g., "Churn Doubled in Q4", not "Churn by Quarter")
- Remove chart junk: gridlines on only one axis, no border box, no 3D effects
- Sort bar charts by value unless the x-axis is inherently ordered (e.g., time, ordinal scale)
- Never use a pie chart with more than 5 slices; use a bar chart instead
- Keep the y-axis starting at zero for bar charts—truncated axes exaggerate differences
- Add data labels directly on bars/lines when the audience needs exact values
- Use consistent color encoding across all charts in a report

## Common Mistakes
- Dual y-axes: almost always misleading; use two separate charts instead
- 3D charts: never—they distort proportions
- Rainbow color palettes: hard to read and inaccessible; use 2–4 purposeful colors
- Plotting time on a categorical (non-ordered) axis—always use a proper date axis
- Omitting axis units (is that revenue in dollars, thousands, or millions?)
- Pie charts with thin slivers—merge small categories into "Other"
- Connecting non-continuous data with lines (e.g., survey responses from different years)

## Tips & Tricks
- `sns.set_style('whitegrid')` gives clean defaults in seaborn with one line
- Use `ax.spines[['top', 'right']].set_visible(False)` to immediately make matplotlib charts look modern
- For colorblind-safe palettes in seaborn, use `palette='colorblind'`
- Add a thin horizontal line at y=0 for charts with negative values: `ax.axhline(0, color='black', linewidth=0.8)`
- Chart.js's `tension: 0.3` makes line charts look smoother without being misleading
- Export at 150+ DPI for crisp results in presentations: `plt.savefig("chart.png", dpi=150)`

## Related Skills
- [data-analyst](../../data/data-analyst/SKILL.md)
- [dashboard-designer](../../data/dashboard-designer/SKILL.md)
- [data-cleaner](../../data/data-cleaner/SKILL.md)
