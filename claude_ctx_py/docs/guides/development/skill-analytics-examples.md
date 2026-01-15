---
layout: default
title: Skill Analytics Examples
nav_order: 7
---

# Skill Analytics Examples

Comprehensive examples and scenarios for using skill analytics to optimize performance and track effectiveness.

## Overview

The skill analytics system provides deep insights into skill usage, effectiveness, ROI, and optimization opportunities. This guide demonstrates practical examples for leveraging analytics to improve your agent ecosystem.

**Key Analytics Features:**
- Effectiveness scoring (0-100 scale)
- ROI calculations (cost savings, token efficiency)
- Trending analysis (7/30/90 day periods)
- Correlation discovery (frequently co-activated skills)
- Usage recommendations
- Export capabilities (JSON, CSV, text)

---

## Quick Start Examples

### Example 1: View All Skill Metrics

```bash
cortex skills metrics

# Output:
# Skill Metrics Summary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Skill                              Act.  Tokens   Success  Last Used
# ─────────────────────────────────────────────────────────────────────
# api-design-patterns                 42   105,200   95.2%   2025-10-17
# microservices-patterns              38    97,600   92.1%   2025-10-17
# kubernetes-deployment-patterns      27    68,400   89.6%   2025-10-16
# python-testing-patterns             23    45,600   91.3%   2025-10-17
# event-driven-architecture           19    64,600   88.4%   2025-10-15
#
# Total Skills: 18
# Total Activations: 247
# Total Tokens Saved: 652,800
# Estimated Cost Savings: $1.96
```

### Example 2: View Specific Skill Metrics

```bash
cortex skills metrics api-design-patterns

# Output:
# Skill: api-design-patterns
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Usage Statistics:
#   Activation Count:    42
#   Total Tokens Saved:  105,200
#   Avg Tokens/Use:      2,505
#   Success Rate:        95.2%
#   Last Activated:      2025-10-17 14:23:15 UTC
#
# Performance Metrics:
#   Effectiveness Score: 87.3/100
#   Cost Saved:          $0.3156
#   Cost per Activation: $0.0075
#   Efficiency Ratio:    4.2x
#
# Activation Trends:
#   Last 7 days:         12 activations
#   Last 30 days:        42 activations
#   Last 90 days:        42 activations
```

### Example 3: Generate Comprehensive Report

```bash
cortex skills report --format text

# Output:
# ════════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE ANALYTICS REPORT
# Generated: 2025-10-17 15:30:00 UTC
# ════════════════════════════════════════════════════════════════════════════════
#
# EXECUTIVE SUMMARY
# ────────────────────────────────────────────────────────────────────────────────
# Total Skills:       18
# Total Activations:  247
# Total Tokens Saved: 652,800
# Total Cost Saved:   $1.9584
#
# TOP PERFORMING SKILLS (by Effectiveness)
# ────────────────────────────────────────────────────────────────────────────────
# 1. api-design-patterns - Score: 87.3/100, Cost Saved: $0.3156
# 2. microservices-patterns - Score: 84.7/100, Cost Saved: $0.2928
# 3. kubernetes-deployment-patterns - Score: 82.1/100, Cost Saved: $0.2052
# ...
```

---

## Analytics Use Cases

### Use Case 1: Identify High-Value Skills

**Goal:** Find skills that provide maximum value to prioritize for improvement.

```bash
# Method 1: Use effectiveness metric
cortex skills analytics --metric effectiveness

# Output:
# Effectiveness Score
# ══════════════════════════════════════════════════════════════════════
# api-design-patterns           ████████████████████████████████████ 87.3
# microservices-patterns        ██████████████████████████████████ 84.7
# kubernetes-deployment-patterns ████████████████████████████████ 82.1
# python-testing-patterns       ████████████████████████████ 75.4
# event-driven-architecture     ██████████████████████████ 73.8
# ...

# Method 2: Use ROI metric
cortex skills analytics --metric roi

# Output shows skills ranked by cost savings and efficiency
```

**Analysis:**
- Skills with effectiveness >80 are high performers
- Focus improvement efforts on mid-range (60-80) skills
- Investigate skills <60 for potential issues

### Use Case 2: Track Skill Adoption

**Goal:** Monitor how new skills are being adopted over time.

```bash
# View trending skills over last 30 days
cortex skills trending --days 30

# Output:
# Trending Skills (Last 30 Days)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Skill                              Uses  Tokens   Trend
# ─────────────────────────────────────────────────────────────────────
# python-testing-patterns             23   45,600   ↑↑↑ (New)
# react-performance-optimization      18   40,500   ↑↑
# kubernetes-security-policies        15   35,250   ↑
# terraform-best-practices            12   27,600   →
# owasp-top-10                         8   25,600   →
#
# ↑↑↑ Rapidly growing  ↑↑ Growing  ↑ Increasing  → Stable  ↓ Declining
```

**Insights:**
- Newly released skills show adoption rate
- Identify skills gaining traction
- Spot declining usage (potential deprecation candidates)

### Use Case 3: Optimize Token Usage

**Goal:** Identify opportunities to reduce token consumption.

```bash
# View skills by token usage
cortex skills analytics --metric tokens

# Output:
# Tokens Saved
# ══════════════════════════════════════════════════════════════════════
# api-design-patterns           ████████████████████████████ 105,200
# microservices-patterns        █████████████████████████ 97,600
# kubernetes-deployment-patterns █████████████████ 68,400
# event-driven-architecture     ████████████████ 64,600
# ...

# Calculate total efficiency
cortex skills report --format json | jq '.summary.total_tokens_saved'
# Output: 652800
```

**Analysis:**
- High token counts indicate heavily-used skills
- Efficiency ratio shows token savings vs. load cost
- Optimize skills with high activations but low efficiency

### Use Case 4: Discover Skill Correlations

**Goal:** Find skills that are frequently used together to create composite skills.

```bash
# Generate correlation matrix
cortex skills analytics --metric correlations

# Output:
# Skill Correlations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# api-design-patterns frequently activated with:
#   - microservices-patterns (correlation: 0.82)
#   - database-design-patterns (correlation: 0.71)
#   - event-driven-architecture (correlation: 0.65)
#
# kubernetes-deployment-patterns frequently activated with:
#   - helm-chart-patterns (correlation: 0.89)
#   - kubernetes-security-policies (correlation: 0.76)
#   - gitops-workflows (correlation: 0.68)
```

**Action Items:**
- Consider creating composite skills for high correlations (>0.75)
- Example: "backend-api-design" combining api-design + microservices
- Example: "k8s-deployment-suite" combining k8s patterns

### Use Case 5: Monitor Success Rates

**Goal:** Identify skills with low success rates that need improvement.

```bash
# View success rates
cortex skills analytics --metric success_rate

# Output:
# Success Rate (%)
# ══════════════════════════════════════════════════════════════════════
# api-design-patterns           ███████████████████████████████ 95.2
# python-testing-patterns       ██████████████████████████████ 91.3
# microservices-patterns        █████████████████████████████ 92.1
# event-driven-architecture     ████████████████████████████ 88.4
# terraform-best-practices      ██████████████████ 58.3  ⚠
# ...

# Get recommendations
cortex skills report --format text | grep -A 5 "RECOMMENDATIONS"

# Output:
# RECOMMENDATIONS
# ────────────────────────────────────────────────────────────────────────
# 1. Review 'terraform-best-practices' - low success rate (58.3%).
#    May need updates or refinement.
# 2. Consider using 'kubernetes-security-policies' more often
#    (effectiveness: 82.5/100, only 15 uses)
```

**Analysis:**
- Success rate <70% indicates potential issues
- Review skill content for clarity
- Check if activation triggers are too broad

---

## Advanced Analytics Scenarios

### Scenario 1: A/B Testing Skill Versions

**Setup:** Testing api-design-patterns v1.2.0 vs v2.0.0

```bash
# Track metrics for both versions
cortex skills metrics api-design-patterns@1.2.0
cortex skills metrics api-design-patterns@2.0.0

# Compare effectiveness
# v1.2.0: Effectiveness 84.2/100, Success Rate: 92.1%
# v2.0.0: Effectiveness 87.3/100, Success Rate: 95.2%

# Decision: v2.0.0 shows improvement, proceed with full rollout
```

### Scenario 2: ROI Analysis for Skill Investment

**Goal:** Determine if creating new skills is worthwhile.

```bash
# Calculate total ROI
cortex skills report --format json | \
  jq '.summary | {
    total_skills,
    total_activations,
    total_cost_saved,
    avg_cost_per_skill: (.total_cost_saved / .total_skills),
    cost_per_activation: (.total_cost_saved / .total_activations)
  }'

# Output:
# {
#   "total_skills": 18,
#   "total_activations": 247,
#   "total_cost_saved": 1.9584,
#   "avg_cost_per_skill": 0.1088,
#   "cost_per_activation": 0.0079
# }
```

**Analysis:**
- Average $0.11 saved per skill
- $0.0079 saved per activation
- Over 1000 activations/month = ~$8/month savings
- ROI positive after 3 months of development time

### Scenario 3: Skill Lifecycle Management

**Goal:** Identify skills at different lifecycle stages.

```bash
# Export detailed analytics
cortex skills report --format json > analytics.json

# Analyze lifecycle stages
cat analytics.json | jq -r '.skills | to_entries[] |
  select(.value.basic_metrics.activation_count < 5) |
  "\(.key) - New/Underutilized (only \(.value.basic_metrics.activation_count) uses)"'

# Output:
# security-testing-patterns - New/Underutilized (only 3 uses)
# threat-modeling-techniques - New/Underutilized (only 2 uses)

# Find stale skills (not used in 30+ days)
cat analytics.json | jq -r '.skills | to_entries[] |
  select(.value.trends."30_days" == 0) |
  "\(.key) - Stale (no uses in 30 days)"'
```

**Lifecycle Actions:**
- **New (<5 uses):** Promote through documentation and examples
- **Growing (increasing trend):** Monitor and support
- **Mature (stable high usage):** Maintain and optimize
- **Declining (decreasing trend):** Investigate causes
- **Stale (0 uses in 30 days):** Consider deprecation

### Scenario 4: Cost-Benefit Analysis for Skill Optimization

**Goal:** Prioritize which skills to optimize for maximum impact.

```bash
# Calculate optimization priority score
cortex skills report --format json | \
  jq -r '.skills | to_entries[] |
  {
    skill: .key,
    activations: .value.basic_metrics.activation_count,
    effectiveness: .value.effectiveness_score,
    potential_impact: (.value.basic_metrics.activation_count * (100 - .value.effectiveness_score))
  } |
  select(.potential_impact > 100) |
  "\(.skill): Impact Score = \(.potential_impact | round)"' | \
  sort -t= -k2 -nr

# Output (sorted by impact):
# terraform-best-practices: Impact Score = 501
# event-driven-architecture: Impact Score = 498
# kubernetes-security-policies: Impact Score = 267
# ...
```

**Priority Formula:**
```
Impact Score = Activations × (100 - Effectiveness)

High score = High usage + Room for improvement
```

**Actions:**
- Optimize skills with highest impact scores first
- Focus on improving effectiveness through:
  - Better examples
  - Clearer explanations
  - Updated patterns
  - Fixed errors

---

## Export and Integration Examples

### Example 1: Export to CSV for Spreadsheet Analysis

```bash
# Export all metrics to CSV
cortex skills report --format csv

# Output file: ~/.claude/.metrics/exports/analytics_20251017_153000.csv
# Import into Excel/Google Sheets for custom analysis
```

**CSV Structure:**
```csv
Skill Name,Activation Count,Total Tokens Saved,Avg Tokens,Success Rate,Last Activated,Cost Saved ($),Effectiveness Score
api-design-patterns,42,105200,2505,92.10%,2025-10-17 14:23:15,$0.3156,87.30
microservices-patterns,38,97600,2568,92.10%,2025-10-17 13:45:22,$0.2928,84.70
...
```

### Example 2: JSON Export for Programmatic Analysis

```bash
# Export to JSON
cortex skills report --format json > analytics.json

# Example: Find skills with effectiveness > 85
cat analytics.json | jq -r '
  .skills |
  to_entries[] |
  select(.value.effectiveness_score > 85) |
  "\(.key): \(.value.effectiveness_score)"
'

# Output:
# api-design-patterns: 87.3
# microservices-patterns: 84.7
```

### Example 3: Integration with Monitoring Systems

```bash
# Create metrics endpoint for Prometheus/Grafana
cat << 'EOF' > /tmp/skill_metrics.sh
#!/bin/bash
# Generate Prometheus metrics from skill analytics

cortex skills report --format json | jq -r '
  .skills | to_entries[] |
  "# TYPE skill_activations gauge\n" +
  "skill_activations{skill=\"\(.key)\"} \(.value.basic_metrics.activation_count)\n" +
  "# TYPE skill_effectiveness gauge\n" +
  "skill_effectiveness{skill=\"\(.key)\"} \(.value.effectiveness_score)\n" +
  "# TYPE skill_cost_saved gauge\n" +
  "skill_cost_saved{skill=\"\(.key)\"} \(.value.roi.cost_saved)"
'
EOF

chmod +x /tmp/skill_metrics.sh

# Run and collect metrics
/tmp/skill_metrics.sh > /var/lib/prometheus/node_exporter/skill_metrics.prom
```

### Example 4: Daily Analytics Email Report

```bash
# Create cron job for daily email report
cat << 'EOF' > /usr/local/bin/skill-analytics-report
#!/bin/bash
# Daily skill analytics report

REPORT_FILE="/tmp/skill_report_$(date +%Y%m%d).txt"

cortex skills report --format text > "$REPORT_FILE"

# Email report
mail -s "Daily Skill Analytics Report - $(date +%Y-%m-%d)" \
     user@example.com < "$REPORT_FILE"

# Cleanup
rm "$REPORT_FILE"
EOF

chmod +x /usr/local/bin/skill-analytics-report

# Add to crontab (daily at 8 AM)
# 0 8 * * * /usr/local/bin/skill-analytics-report
```

---

## Visualization Examples

### Example 1: ASCII Bar Charts in Terminal

```bash
# Visualize activation counts
cortex skills analytics --metric activations

# Output:
# Skill Activations
# ══════════════════════════════════════════════════════════════════════
# api-design-patterns           ██████████████████████████████████ 42
# microservices-patterns        ████████████████████████████████ 38
# kubernetes-deployment-patterns ████████████████████ 27
# python-testing-patterns       ████████████████ 23
# event-driven-architecture     █████████████ 19
# kubernetes-security-policies  ██████████ 15
# react-performance-optimization ████████ 12
# terraform-best-practices      ██████ 9
# ...
```

### Example 2: Trending Visualization

```bash
# Show 7-day trends
cortex skills trending --days 7

# Output with trend indicators:
# Trending Skills (Last 7 Days)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# api-design-patterns          ▁▂▃▅▆▇█  12 activations  [+40%]
# python-testing-patterns      ▁▁▂▄▅▇█   8 activations  [+60%]
# microservices-patterns       ▃▄▅▅▆▆█  10 activations  [+25%]
# event-driven-architecture    ▂▃▃▄▄▄▅   5 activations  [+15%]
#
# Legend: ▁ Low → █ High
```

---

## Troubleshooting Analytics

### Issue 1: No Metrics Available

```bash
cortex skills metrics

# Output:
# No metrics available. Use skills to generate analytics.

# Cause: Skills haven't been activated yet
# Solution: Activate agents that use skills, or wait for natural usage
```

### Issue 2: Metrics Reset Accidentally

```bash
# Check if metrics were recently reset
ls -la ~/.claude/.metrics/skills/

# Restore from backup if available
cp ~/.claude/.metrics/skills/metrics.json.backup \
   ~/.claude/.metrics/skills/metrics.json
```

### Issue 3: Incomplete Activation Data

```bash
# Validate metrics file
cortex skills metrics --validate

# Output shows any corrupted or missing data
# Rebuild metrics from activation logs if needed
```

---

## Best Practices

### For Regular Monitoring

1. **Weekly Review**
   ```bash
   cortex skills trending --days 7
   cortex skills analytics --metric effectiveness
   ```

2. **Monthly Analysis**
   ```bash
   cortex skills report --format text > monthly_report.txt
   # Review and act on recommendations
   ```

3. **Quarterly Deep Dive**
   ```bash
   cortex skills report --format csv
   # Import into spreadsheet for detailed analysis
   # Plan skill improvements for next quarter
   ```

### For Skill Development

1. **Track New Skills**
   - Monitor adoption over first 30 days
   - Target: 10+ activations in first month
   - Effectiveness target: >70 by end of month

2. **Measure Impact**
   - Calculate tokens saved per activation
   - Track success rate trends
   - Gather user feedback

3. **Iterate Based on Data**
   - Low success rate? → Improve clarity
   - Low usage? → Better activation triggers
   - High correlation? → Consider combining skills

---

## See Also

- [Skill Versioning README](./skill-versioning-README.md) - Version management
- [Skills Guide](../skills.md) - General skills documentation
- [Architecture](./architecture.md) - System architecture details
