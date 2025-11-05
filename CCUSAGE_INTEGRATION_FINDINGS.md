# ccusage Integration - API Exploration Findings

## Executive Summary

**Good News**: The codebase already has **extensive token tracking infrastructure** in place. A ccusage integration would build on top of existing metrics rather than starting from scratch.

**Key Finding**: There's NO direct API client to Claude/Anthropic services - this tool operates at a **higher abstraction level** (CLI wrapper around Claude Code), so usage data would need to come from:
1. Claude Code's internal usage APIs (if exposed)
2. Manual token estimation based on skill content size
3. External ccusage CLI integration

## Current Token Tracking Infrastructure

### ✅ Already Implemented

#### 1. **Token Cost Constant** (`analytics.py:21`)
```python
TOKEN_COST_PER_1K = 0.003  # $0.003 per 1K tokens
```

#### 2. **Metrics Storage System** (`~/.claude/.metrics/skills/`)
- `stats.json` - Summary metrics per skill
- `activations.json` - Detailed activation records (last 1000)

#### 3. **Activation Tracking** (`metrics.py:80-125`)
```python
def record_activation(skill_name: str, tokens_used: int, success: bool)
```
Tracks:
- `activation_count`: Number of times activated
- `total_tokens_saved`: Cumulative tokens saved
- `avg_tokens`: Average tokens per activation
- `success_rate`: Success percentage
- `last_activated`: Timestamp

#### 4. **Detailed Activation Records** (`metrics.py:160-241`)
```python
def record_detailed_activation(skill_name: str, context: Dict[str, Any])
```
Tracks:
- `activation_id`: UUID
- `tokens_loaded`: Tokens in skill content
- `tokens_saved`: Estimated tokens saved
- `duration_ms`: Execution time
- `agent`: Activating agent
- `task_type`, `project_type`: Context
- `relevance_score`: How relevant (0-1)
- `user_satisfaction`: Rating (1-5)

#### 5. **ROI Calculator** (`analytics.py:85-136`)
```python
def calculate_roi(skill_name: str, claude_dir: Path) -> Dict
```
Returns:
- `cost_saved`: Dollar amount saved
- `tokens_saved`: Total tokens
- `activations`: Usage count
- `cost_per_activation`: Average cost per use
- `efficiency_ratio`: tokens_saved / tokens_loaded

#### 6. **Analytics Dashboard** (`analytics.py`)
- Effectiveness scoring (0-100)
- Trending skills analysis
- Correlation matrices
- Impact reports

### 📋 Comprehensive Analytics Schema

The project has a **879-line JSON schema** (`skills/analytics.schema.json`) defining:

#### Token Usage Tracking (Lines 212-234)
```json
"token_usage": {
  "input_tokens": 0,
  "output_tokens": 0,
  "total_tokens": 0,
  "efficiency_score": 0.0-1.0
}
```

#### Session Aggregation (Lines 519-556)
```json
"aggregated_metrics": {
  "total_token_usage": 0,
  "total_tool_calls": 0,
  "total_files_modified": 0,
  "total_commands_executed": 0
}
```

## What's Missing for ccusage Integration

### 1. **No Direct API Client**
- No `anthropic` SDK dependency
- No API key management
- No direct API calls to Claude services

### 2. **Token Data Sources**
Current metrics track `tokens_loaded` and `tokens_saved` but these are:
- **Estimated** based on skill content size
- **Not actual usage** from Claude API responses

### 3. **Usage Attribution**
Missing:
- Real input/output token counts per API call
- Cost breakdown by model (Haiku vs Sonnet vs Opus)
- Rate limiting information
- Billing cycle tracking

## Integration Approaches

### Option 1: ccusage CLI Integration ⭐ **Recommended**

**Concept**: Wrap ccusage as subprocess to fetch real usage data

**Implementation**:
```python
# claude_ctx_py/ccusage_client.py
import subprocess
import json
from datetime import datetime, timedelta

def get_usage_data(period_days: int = 7) -> Dict[str, Any]:
    """Fetch usage data from ccusage CLI."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)

    result = subprocess.run([
        "ccusage",
        "usage",
        "--start", start_date.strftime("%Y-%m-%d"),
        "--end", end_date.strftime("%Y-%m-%d"),
        "--format", "json"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise CCUsageError(result.stderr)

def sync_usage_to_metrics():
    """Sync ccusage data to local metrics."""
    usage_data = get_usage_data()

    # Map usage to skill activations
    # Store in ~/.claude/.metrics/usage/
    # Correlate with activation timestamps
```

**CLI Commands**:
```bash
# Sync usage data
claude-ctx usage sync

# View current usage
claude-ctx usage current

# Compare estimated vs actual
claude-ctx usage compare
```

### Option 2: Claude Code API Integration

**Concept**: Hook into Claude Code's internal usage APIs (if available)

**Challenge**: Need to investigate Claude Code's extension APIs for usage data access

**Research Needed**:
1. Does Claude Code expose usage APIs to plugins?
2. What format is the data in?
3. Can we subscribe to real-time usage events?

### Option 3: Manual Token Estimation (Current Approach)

**Concept**: Continue using estimated tokens based on content size

**Pros**:
- No external dependencies
- Already implemented
- Works offline

**Cons**:
- Not accurate
- Can't track actual API costs
- No real-time data

## Proposed Feature: Usage Tracking Module

### Architecture

```
claude_ctx_py/
├── usage.py              # Core usage tracking
├── ccusage_client.py     # ccusage CLI wrapper
└── usage_sync.py         # Sync logic

~/.claude/.metrics/
└── usage/
    ├── sessions.json     # Session-level usage
    ├── sync_history.json # Last sync timestamps
    └── budget.json       # Budget tracking
```

### Core Components

#### 1. Usage Data Model
```python
@dataclass
class UsageRecord:
    session_id: str
    timestamp: datetime
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str  # "claude-3-5-sonnet-20241022"
    cost_usd: float
    operation: str  # "skill_activation", "agent_call", etc.
    context: Dict[str, Any]
```

#### 2. Budget Tracking
```python
@dataclass
class Budget:
    daily_limit_usd: float
    weekly_limit_usd: float
    monthly_limit_usd: float
    current_day_spent: float
    current_week_spent: float
    current_month_spent: float
    alert_threshold: float = 0.8  # Alert at 80%
```

#### 3. Usage Analytics
```python
def get_usage_breakdown(period: str = "week") -> Dict:
    """Break down usage by agent, skill, operation type."""

def get_cost_trend(days: int = 30) -> List[Dict]:
    """Get daily cost trend."""

def get_optimization_suggestions() -> List[str]:
    """Suggest ways to reduce costs."""
```

### CLI Integration

```bash
# Current usage
claude-ctx usage current
# → Today: 45,231 tokens ($0.23)
# → This week: 2.3M tokens ($11.50)
# → This month: 8.7M tokens ($43.50)

# Breakdown
claude-ctx usage breakdown --by agent
# → test-automator: 850K tokens ($4.25)
# → code-reviewer: 620K tokens ($3.10)
# → security-auditor: 410K tokens ($2.05)

claude-ctx usage breakdown --by skill
# → python-testing: 320K tokens ($1.60)
# → api-design: 280K tokens ($1.40)

# Budget management
claude-ctx usage budget --daily 10 --weekly 50 --monthly 200
# → Budget set: $10/day, $50/week, $200/month

# Alerts
claude-ctx usage alerts
# → ⚠️  Daily budget at 85% ($8.50 / $10.00)
# → ✅ Weekly budget at 45% ($22.50 / $50.00)

# Sync with ccusage
claude-ctx usage sync
# → Syncing usage data from ccusage...
# → ✓ Synced 234 records
# → Last 7 days: $43.21 actual vs $38.50 estimated

# Compare estimated vs actual
claude-ctx usage compare
# → Accuracy: 89.2%
# → Overestimated: +12% (test-automator)
# → Underestimated: -8% (code-reviewer)
```

### Watch Mode Integration

```python
# claude_ctx_py/watch.py - Add budget awareness

class WatchMode:
    def __init__(
        self,
        auto_activate: bool = True,
        notification_threshold: float = 0.7,
        check_interval: float = 2.0,
        budget_alert_threshold: float = 0.8,  # NEW
    ):
        self.budget_tracker = BudgetTracker()  # NEW

    def _check_budget(self) -> bool:
        """Check if budget exceeded."""
        usage = self.budget_tracker.get_current_usage()

        if usage.daily_percent > self.budget_alert_threshold:
            self._print_notification(
                "💰",
                "Budget Alert",
                f"Daily budget at {usage.daily_percent:.0%}",
                "yellow"
            )
            return False
        return True

    def _check_for_changes(self) -> None:
        # Existing change detection...

        # NEW: Budget check before auto-activation
        if self.auto_activate and not self._check_budget():
            self._print_notification(
                "⏸️",
                "Auto-Activation Paused",
                "Budget threshold reached",
                "yellow"
            )
            return
```

### TUI Integration

Add new view: `usage_view.py`

```python
from textual.widgets import DataTable, ProgressBar

class UsageView(Widget):
    """Usage tracking dashboard in TUI."""

    def compose(self):
        yield Header("💰 Usage & Costs")
        yield BudgetGauges()  # Visual budget meters
        yield UsageBreakdownTable()
        yield CostTrendChart()  # Line chart of daily costs
        yield OptimizationSuggestions()
```

**TUI Keys**:
- Press `9` for Usage view
- Press `U` to sync usage data
- Press `B` to configure budget

## Dependencies

### New Dependencies Needed

```toml
[project.optional-dependencies]
usage = [
    "anthropic>=0.40.0",  # If using Anthropic SDK directly
    "httpx>=0.27.0",      # For API calls if needed
]
```

**Or** no new dependencies if using ccusage CLI wrapper (subprocess only)

## Implementation Roadmap

### Phase 1: Foundation (2-3 days)
- [ ] Create `usage.py` module with data models
- [ ] Create `ccusage_client.py` wrapper
- [ ] Add `usage` subcommand to CLI
- [ ] Basic `claude-ctx usage current` command

### Phase 2: Tracking (2-3 days)
- [ ] Session-level usage tracking
- [ ] Usage breakdown by agent/skill
- [ ] Sync mechanism with ccusage
- [ ] Historical data storage

### Phase 3: Budget (2 days)
- [ ] Budget configuration
- [ ] Alert system
- [ ] Watch mode integration
- [ ] Cost optimization suggestions

### Phase 4: Analytics (2-3 days)
- [ ] Usage trends and charts
- [ ] Accuracy comparison (estimated vs actual)
- [ ] ROI recalculation with real data
- [ ] TUI usage view

### Phase 5: Intelligence Integration (2 days)
- [ ] Feed usage data into PatternLearner
- [ ] Cost-aware agent recommendations
- [ ] Budget-conscious auto-activation
- [ ] Optimization learning

## Example User Flows

### Flow 1: Daily Check
```bash
$ claude-ctx usage current
╭─────────────── Usage Summary ───────────────╮
│ Today                                       │
│   Tokens: 45,231 ($0.23)                   │
│   Calls: 23                                 │
│   Peak: 10:30 AM                            │
│                                             │
│ This Week                                   │
│   Tokens: 2.3M ($11.50)                    │
│   Daily Avg: 328K ($1.64)                  │
│   Budget: 23% used                          │
│                                             │
│ Top Consumers                               │
│   test-automator    850K ($4.25) ████████  │
│   code-reviewer     620K ($3.10) ██████    │
│   security-auditor  410K ($2.05) ████      │
╰─────────────────────────────────────────────╯
```

### Flow 2: Budget Alert
```bash
$ claude-ctx ai watch

[10:33:12] 💰 Daily budget at 85% ($8.50 / $10.00)
           Consider:
           • Reduce auto-activation threshold
           • Batch operations
           • Review agent efficiency
```

### Flow 3: Optimization
```bash
$ claude-ctx usage optimize

💡 Optimization Suggestions:

1. **test-automator** (850K tokens, $4.25)
   → Avg 15K tokens per activation
   → Suggestion: Break into smaller test suites
   → Potential savings: 20% ($0.85/week)

2. **code-reviewer** (620K tokens, $3.10)
   → Often reviews same files multiple times
   → Suggestion: Cache review results
   → Potential savings: 30% ($0.93/week)

3. **Auto-activation** threshold: 70%
   → 12 auto-activations this week
   → Suggestion: Increase to 80% for non-critical agents
   → Potential savings: 15% ($1.73/week)

Total potential savings: $3.51/week ($15.21/month)
```

## Next Steps

1. **Research ccusage API** - Investigate ccusage CLI output format
2. **Prototype sync** - Build basic ccusage → metrics sync
3. **User feedback** - Ask which integration approach to prioritize
4. **Implement Phase 1** - Basic usage tracking

## Questions to Answer

1. Does Claude Code expose usage/billing APIs to plugins?
2. What format does ccusage output? Can we parse it?
3. Should we support multiple cost models (Anthropic, OpenAI, etc.)?
4. Real-time tracking vs periodic sync?
5. Privacy concerns with usage data storage?

---

**Ready to implement?** Let me know which approach to start with!
