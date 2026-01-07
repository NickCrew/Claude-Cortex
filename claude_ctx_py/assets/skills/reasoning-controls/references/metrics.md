# Reference: metrics

# /reasoning:metrics - Reasoning Analytics Dashboard

## Personas (Thinking Modes)
- **data-analyst**: Metrics interpretation, trend analysis, pattern recognition, statistical insights
- **performance-engineer**: Reasoning efficiency, execution time analysis, optimization recommendations
- **cost-optimizer**: Budget tracking, cost-benefit analysis, resource allocation guidance

## Delegation Protocol

**This command does NOT delegate** - Metrics display is direct data presentation.

**Why no delegation**:
- ❌ Fast metrics retrieval and calculation
- ❌ Simple dashboard generation
- ❌ Direct data formatting and visualization
- ❌ No complex analysis required (just presentation)

**All work done directly**:
- Read metrics from command history/logs
- Calculate effectiveness scores
- Format dashboard output
- Generate recommendations based on patterns

**Note**: Personas guide metric interpretation (analyst for insights, performance for efficiency, optimizer for cost).

## Tool Coordination
- **Read**: Command execution history and metrics data (direct)
- **Direct calculation**: Effectiveness scores and patterns (direct)
- **Direct output**: Dashboard generation (direct)
- **No delegation needed**: Simple data presentation

## Triggers
- Need to understand reasoning effectiveness and costs
- Optimization of reasoning depth for specific task types
- Budget planning and cost analysis
- Performance tuning of reasoning strategies

## Usage
```
/reasoning:metrics [--command <name>] [--timeframe 7d|30d|all] [--export json|markdown|csv]
```

## Behavioral Flow
1. **Collect**: Gather reasoning metrics from command execution history
2. **Analyze**: Calculate effectiveness scores and patterns
3. **Visualize**: Generate dashboard with key metrics and trends
4. **Recommend**: Suggest optimal reasoning configurations
5. **Export**: Output metrics in requested format for analysis

Key behaviors:
- Track token usage by reasoning level and command
- Measure success rates and confidence scores
- Identify optimal depth/budget combinations
- Detect patterns in escalation triggers

## Metrics Tracked

### Token Usage Metrics

**By Reasoning Depth:**
- Low (2K): Actual usage, average, success rate
- Medium (4K): Actual usage, average, success rate
- High (10K): Actual usage, average, success rate
- Ultra (32K): Actual usage, average, success rate
- Extended (128K): Actual usage, average, success rate

**By Budget Level:**
- Allocated vs actual consumption
- Budget efficiency (quality per token)
- Underutilization percentage
- Overrun frequency

### Quality Metrics

**Success Indicators:**
- Task completion rate by depth level
- Average confidence score per level
- First-attempt success rate
- Escalation frequency

**Effectiveness Scores:**
- Quality per token (QPT) ratio
- Solution efficiency index
- Reasoning depth optimization score

### Cost Metrics

**Spending Analysis:**
- Total tokens consumed (input + output)
- Cost by reasoning level
- Cost per command type
- Monthly burn rate projection

**ROI Analysis:**
- Cost vs quality trade-offs
- Optimal budget recommendations
- Overspending detection

### MCP Server Activation

**Usage Patterns:**
- Sequential: Activation frequency, avg tokens
- Context7: Activation frequency, pattern lookups
- Codanna: Activation frequency, symbol operations
- Combined activations per depth level

## Dashboard Sections

### 1. Executive Summary
```
Reasoning Metrics Summary (Last 30 Days)
=========================================
Total Requests:           147
Total Tokens:             892,450
Total Cost:              $2.68
Avg Confidence:          0.87
Success Rate:            94.3%

Top Command:             /analyze:code (52 requests)
Most Effective Depth:    High (10K) - 96% success
Budget Efficiency:       87% (optimal usage)
```

### 2. Depth Distribution
```
Reasoning Depth Usage
=====================
Low (2K):       ▓▓▓▓▓▓▓▓░░░░░░░░  15% (22 requests)
Medium (4K):    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  38% (56 requests)
High (10K):     ▓▓▓▓▓▓▓▓▓▓▓▓░░░░  32% (47 requests)
Ultra (32K):    ▓▓▓▓▓▓░░░░░░░░░░  12% (18 requests)
Extended (128K): ▓░░░░░░░░░░░░░░   3% (4 requests)
```

### 3. Cost Breakdown
```
Cost Analysis by Depth Level
=============================
Depth Level     Requests  Avg Tokens  Avg Cost   Total Cost
--------------------------------------------------------------
Low (2K)            22      1,847     $0.006     $0.12
Medium (4K)         56      3,921     $0.012     $0.67
High (10K)          47      9,234     $0.028     $1.31
Ultra (32K)         18     28,901     $0.087     $1.56
Extended (128K)      4    112,450     $0.337     $1.35
--------------------------------------------------------------
TOTAL              147     (avg 6,071)           $5.01
```

### 4. Success Rate Analysis
```
Success Rates by Depth
======================
Depth Level     Success   Failed   Escalated  Confidence
----------------------------------------------------------
Low (2K)         81.8%    13.6%      4.5%       0.78
Medium (4K)      92.9%     5.4%      1.8%       0.84
High (10K)       97.9%     2.1%      0.0%       0.91
Ultra (32K)     100.0%     0.0%      0.0%       0.95
Extended (128K) 100.0%     0.0%      0.0%       0.98
```

### 5. Command-Specific Metrics
```
Top Commands by Usage
=====================
Command              Requests  Avg Depth  Success  Avg Cost
------------------------------------------------------------
/analyze:code            52     High      96.2%    $0.031
/design:system           28     Ultra     100%     $0.094
/dev:implement           24     Medium    91.7%    $0.014
/reasoning:adjust        19     N/A       100%     $0.008
/orchestrate:spawn       14     High      92.9%    $0.029
```

### 6. Optimization Recommendations
```
Recommendations
===============
✓ /analyze:code: Currently optimal at High depth
  → 96% success, $0.031/request, rarely escalates

⚠ /dev:implement: Consider Medium→High for 8% tasks
  → 8% escalation rate, could start higher for complex tasks

⚠ Budget efficiency: 13% overallocation detected
  → 19 requests used <50% of allocated budget
  → Consider dynamic budgeting with --auto-adjust

✓ Extended thinking: High ROI on critical tasks
  → 100% success on 4 complex system designs
  → $1.35 total cost prevented 3+ days of rework
```

## Export Formats

### JSON Export
```json
{
  "summary": {
    "total_requests": 147,
    "total_tokens": 892450,
    "total_cost_usd": 2.68,
    "avg_confidence": 0.87,
    "success_rate": 0.943
  },
  "by_depth": [
    {
      "level": "medium",
      "tokens": 4000,
      "requests": 56,
      "success_rate": 0.929,
      "avg_tokens_used": 3921,
      "avg_cost_usd": 0.012
    }
  ],
  "by_command": [...],
  "recommendations": [...]
}
```

### Markdown Export
Full dashboard rendered as markdown table for documentation.

### CSV Export
```csv
timestamp,command,depth,tokens_allocated,tokens_used,success,confidence,cost_usd
2025-10-18 14:32,analyze:code,high,10000,9234,true,0.92,0.028
2025-10-18 15:45,dev:implement,medium,4000,3821,true,0.88,0.011
...
```

## Integration Points

### With /reasoning:budget
```bash
# Get metrics to inform budget decisions
/reasoning:metrics --command analyze:code
# Shows: High (10K) optimal for analyze:code

# Set budget based on metrics
/reasoning:budget 10000
```

### With /reasoning:adjust
```bash
# Track escalation patterns
/reasoning:metrics --export json
# Analyze: Which commands escalate most frequently?
# Adjust default depths accordingly
```

### With --auto-escalate
```bash
# Metrics inform auto-escalation triggers
# High escalation rate → lower initial threshold
# Low escalation rate → higher initial threshold
```

## Tool Coordination
- **Read**: Access metrics storage (JSON files)
- **Grep**: Pattern analysis in usage logs
- **Bash**: Generate visualizations with plotting tools
- **Write**: Export formatted metrics reports

## Key Patterns
- **Trend Analysis**: Usage over time → budget optimization
- **Command Profiling**: Per-command optimal depth discovery
- **Cost Optimization**: Identify overallocation and underutilization
- **Quality Tracking**: Monitor confidence and success correlations

## Examples

### Overall Dashboard
```bash
/reasoning:metrics
# Show complete dashboard for last 30 days
# All metrics, recommendations, and trends
```

### Command-Specific Analysis
```bash
/reasoning:metrics --command analyze:code
# Deep dive into analyze:code performance
# Optimal depth, success patterns, cost analysis
```

### Export for Analysis
```bash
/reasoning:metrics --timeframe all --export json > metrics.json
# Export all historical data as JSON
# Use for custom analysis or visualization
```

### Cost Planning
```bash
/reasoning:metrics --timeframe 30d --export csv
# 30-day cost analysis
# Budget planning and trend projection
```

## Boundaries

**Will:**
- Track and analyze reasoning effectiveness metrics
- Provide cost analysis and optimization recommendations
- Export metrics in multiple formats for analysis
- Identify patterns and suggest improvements

**Will Not:**
- Automatically change reasoning settings (requires user action)
- Access or modify actual command execution
- Guarantee future performance based on historical metrics
- Store sensitive data from command outputs

## Privacy & Data

**Metrics Stored:**
- Command name, timestamp, depth level
- Token usage, cost calculations
- Success/failure status, confidence scores
- MCP server activations

**NOT Stored:**
- Actual command inputs or outputs
- File contents or code being analyzed
- User identifiers or session data
- Sensitive configuration values

**Storage Location:**
- `~/.claude/.metrics/reasoning/`
- JSON format, user-readable
- Can be deleted anytime without affecting functionality

## Related Commands

- `/reasoning:budget` - Set thinking token budgets
- `/reasoning:adjust` - Runtime depth control
- `/analyze:code --reasoning-profile` - Domain optimization
