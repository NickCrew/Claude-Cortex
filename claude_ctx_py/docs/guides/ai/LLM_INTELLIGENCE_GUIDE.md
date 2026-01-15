# LLM Intelligence Guide

## Overview

The LLM Intelligence feature uses Claude API to provide advanced reasoning about your development context and agent recommendations. Unlike pattern matching or semantic embeddings, LLM analysis actually understands the nuance of what you're working on.

## Quick Start

### 1. Installation

```bash
pip install cortex-py[llm]
```

This installs the Anthropic SDK for Claude API access.

### 2. Configuration

Set your API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or store it in your shell config (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.zshrc
source ~/.zshrc
```

### 3. Enable LLM Features

```bash
cortex config set ai.use_llm true
```

### 4. Start Using

```bash
# Get recommendations with LLM analysis
cortex ai recommend
```

## How It Works

### Request Flow

```
New Context
     │
     ▼
Semantic Matching (fast, free)
     │
     ├─ Confidence > threshold (0.5)
     │  └─ Return recommendations
     │
     └─ Confidence < threshold
        └─ Call Claude API for analysis
           └─ Return LLM recommendations
```

### Hybrid Strategy

The system is designed to minimize API costs while maximizing quality:

1. **Try Fast Methods First**: Semantic matching (50ms, free)
2. **Use LLM Only When Needed**: When confidence < threshold
3. **Fall Back to Patterns**: If LLM unavailable or API fails

This means:
- 80-90% of the time: Use fast semantic matching
- 10-20% of the time: Call Claude API for deep analysis
- Average cost: ~$0.0005-0.001 per session

## Configuration

### Core Settings

```bash
# Enable/disable LLM analysis
cortex config set ai.use_llm true

# Confidence threshold for calling LLM (0.0-1.0)
# Default: 0.5 (call LLM if semantic confidence < 50%)
# Lower value = more LLM calls (higher cost, better quality)
# Higher value = fewer LLM calls (lower cost, lower quality)
cortex config set ai.llm_threshold 0.5

# Budget limit (USD per month)
cortex config set ai.llm_budget_limit 10.00

# Auto-activate high-confidence recommendations
cortex config set ai.auto_activate true

# Confidence threshold for auto-activation (0.0-1.0)
# Default: 0.8 (auto-activate if confidence > 80%)
cortex config set ai.auto_activate_threshold 0.8
```

### Advanced Settings

```bash
# Model selection (affects cost and quality)
# claude-opus-4-1 (most capable, highest cost)
# claude-sonnet-4-20250514 (balanced, default)
# claude-haiku-3-5 (fast, lowest cost)
cortex config set ai.llm_model claude-sonnet-4-20250514

# Max tokens for LLM response (affects cost)
# Default: 1024
cortex config set ai.llm_max_tokens 1024

# Temperature (affects reasoning creativity, 0.0-1.0)
# 0.0 = deterministic, 1.0 = creative
# Default: 0.3 (mostly deterministic)
cortex config set ai.llm_temperature 0.3

# Disable LLM for watch mode (prevents surprise costs)
cortex config set ai.use_llm_in_watch_mode false
```

## Pricing & Costs

### API Pricing

Claude API uses input and output tokens:

| Model | Input Cost | Output Cost |
|-------|-----------|------------|
| Claude Opus 4.1 | $15/M tokens | $45/M tokens |
| Claude Sonnet 4 (default) | $3/M tokens | $15/M tokens |
| Claude Haiku 3.5 | $0.80/M tokens | $4/M tokens |

### Typical Costs per Analysis

```
Scenario 1: Simple Analysis (Haiku)
  Input: ~200 tokens
  Output: ~100 tokens
  Cost: $0.00016 + $0.0004 = $0.00056

Scenario 2: Complex Analysis (Sonnet)
  Input: ~500 tokens
  Output: ~300 tokens
  Cost: $0.0015 + $0.0045 = $0.006

Scenario 3: Full Analysis (Opus)
  Input: ~800 tokens
  Output: ~500 tokens
  Cost: $0.012 + $0.0225 = $0.0345
```

### Monthly Estimates

With default settings (50% LLM call rate):

- **Light usage** (10 sessions/day): ~$0.10/month
- **Medium usage** (30 sessions/day): ~$0.30/month
- **Heavy usage** (100 sessions/day): ~$1.00/month

## Understanding Recommendations

### Recommendation Structure

```json
{
  "agent_name": "security-auditor",
  "confidence": 0.95,
  "reason": "Authentication code detected in changed files. Previous similar sessions used security-auditor successfully.",
  "urgency": "high",
  "auto_activate": true
}
```

**Fields**:
- `agent_name`: The recommended agent (exact match to available agents)
- `confidence`: 0.0-1.0, higher = more certain
- `reason`: Why this agent was recommended
- `urgency`: low/medium/high/critical
- `auto_activate`: Whether to activate automatically

### Confidence Interpretation

| Confidence | Meaning | Action |
|-----------|---------|--------|
| 0.90-1.00 | Very certain | Auto-activate (if enabled) |
| 0.70-0.90 | Quite confident | Consider activating |
| 0.50-0.70 | Moderately confident | Review before activating |
| 0.30-0.50 | Somewhat uncertain | Verify manually |
| 0.00-0.30 | Unlikely match | Probably ignore |

### Urgency Levels

- **critical**: Agent should be auto-activated immediately
- **high**: Agent should be activated before deployment
- **medium**: Agent could help but not essential
- **low**: Agent provides optional enhancement

## Best Practices

### 1. Start Conservative

Disable LLM initially while tuning thresholds:

```bash
cortex config set ai.use_llm false

# After a week, enable with high threshold
cortex config set ai.use_llm true
cortex config set ai.llm_threshold 0.3  # Only use LLM if semantic confidence very low
```

### 2. Monitor Costs

Check your Anthropic usage periodically:

```bash
# View last week's recommendations
cortex session list --since "7 days ago" | grep llm

# Check your API usage
# Visit https://console.anthropic.com/account/billing
```

### 3. Tune Thresholds

Higher threshold = fewer LLM calls = lower cost:

```bash
# Conservative (minimum API calls)
cortex config set ai.llm_threshold 0.2  # Only use LLM if < 20% confident

# Balanced (default)
cortex config set ai.llm_threshold 0.5  # Use LLM if < 50% confident

# Aggressive (better quality, higher cost)
cortex config set ai.llm_threshold 0.8  # Use LLM if < 80% confident
```

### 4. Use Budget Controls

Set a monthly budget limit:

```bash
# Limit to $5/month
cortex config set ai.llm_budget_limit 5.00

# Check current spending
cortex stats --period month
```

### 5. Review Recommendations Regularly

```bash
# See what LLM recommended last week
cortex session list --since "7 days ago" \
  | grep -A 5 "llm_recommendations"

# Track which agents LLM recommends most
cortex stats --by agent --source llm
```

## Troubleshooting

### "LLM intelligence not available"

**Cause**: Anthropic package not installed or API key missing

**Solution**:
```bash
# Install package
pip install cortex-py[llm]

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Verify
cortex config get ai
```

### "API key invalid" or "Authentication failed"

**Cause**: Invalid or expired API key

**Solution**:
1. Visit https://console.anthropic.com/account/api-keys
2. Create new key if needed
3. Update: `export ANTHROPIC_API_KEY=sk-ant-...`

### "Rate limit exceeded"

**Cause**: Too many API calls in a short time

**Solution**:
```bash
# Increase threshold to reduce API calls
cortex config set ai.llm_threshold 0.2

# Disable LLM temporarily
cortex config set ai.use_llm false
```

### "Model not found" or "Invalid model"

**Cause**: Specified model doesn't exist or isn't available

**Solution**:
```bash
# Use a valid model
cortex config set ai.llm_model claude-sonnet-4-20250514

# Check available models at:
# https://docs.anthropic.com/claude/reference/getting-started-with-the-api
```

### "Unexpected token in JSON" error

**Cause**: LLM response malformed

**Solution**:
1. Try again (usually transient)
2. Check your configuration
3. File issue with response details (redact API key)

### High costs despite budget limit

**Cause**: Budget limit not set or threshold too low

**Solution**:
```bash
# Set conservative budget
cortex config set ai.llm_budget_limit 1.00

# Increase confidence threshold (fewer API calls)
cortex config set ai.llm_threshold 0.2
```

## Advanced Usage

### Custom Model Selection

Choose based on your needs:

```bash
# For maximum accuracy (slower, more expensive)
cortex config set ai.llm_model claude-opus-4-1

# For balanced performance (default, recommended)
cortex config set ai.llm_model claude-sonnet-4-20250514

# For speed and cost (faster, cheaper)
cortex config set ai.llm_model claude-haiku-3-5
```

### Temperature Tuning

Adjust reasoning creativity:

```bash
# Very deterministic (recommended for agent selection)
cortex config set ai.llm_temperature 0.0

# Slightly creative (good default)
cortex config set ai.llm_temperature 0.3

# Very creative (not recommended for structured tasks)
cortex config set ai.llm_temperature 0.7
```

### Token Limits

Adjust response verbosity (higher = longer, more tokens):

```bash
# Minimal response (saves cost)
cortex config set ai.llm_max_tokens 512

# Balanced response (default)
cortex config set ai.llm_max_tokens 1024

# Detailed response (higher cost)
cortex config set ai.llm_max_tokens 2048
```

### Disable for Specific Modes

Prevent unexpected costs:

```bash
# Don't use LLM in watch mode (frequent checks)
cortex config set ai.use_llm_in_watch_mode false

# Don't use LLM for batch operations
cortex config set ai.use_llm_in_batch false
```

## API Reference

### Python Integration

```python
from claude_ctx_py.intelligence import LLMIntelligence, SessionContext
import os

# Initialize LLM intelligence
llm = LLMIntelligence(available_agents=[
    {"name": "security-auditor", "summary": "Audits security"},
    {"name": "code-reviewer", "summary": "Reviews code"},
])

# Analyze context and get recommendations
result = llm.analyze_and_recommend(
    context={
        "files_changed": ["auth.py", "oauth.py"],
        "file_types": [".py"],
        "directories": ["src/auth"],
        "has_auth": True,
        "has_tests": False,
        "errors_count": 0,
        "test_failures": 0,
    },
    recent_sessions=[
        {"agents": ["security-auditor"], "outcome": "success"},
        {"agents": ["code-reviewer"], "outcome": "success"},
    ]
)

# Extract recommendations and metadata
recommendations = result['recommendations']
metadata = result['metadata']

# Display cost information
print(f"Model used: {metadata['model_name']}")
print(f"Total cost: ${metadata['cost']['total_cost']:.6f}")
if metadata.get('cache_hit'):
    print("✓ Used prompt cache (90% savings)")

# Use recommendations
for rec in recommendations:
    print(f"{rec['agent_name']}: {rec['confidence']:.0%} - {rec['reason']}")
    if rec.get('auto_activate'):
        print(f"  → Auto-activating (urgency: {rec['urgency']})")
```

### Environment Variables

```bash
# API key (required)
ANTHROPIC_API_KEY=sk-ant-...

# Optional overrides
CORTEX_LLM_MODEL=claude-sonnet-4-20250514
CORTEX_LLM_THRESHOLD=0.5
CORTEX_LLM_TEMPERATURE=0.3
CORTEX_LLM_MAX_TOKENS=1024
```

## Integration with Other Features

### With Semantic Matching

```
Context Analysis
  │
  ├─ Semantic Matching (fast)
  │   └─ Confidence: 0.45
  │
  └─ LLM Analysis (called because 0.45 < 0.5)
      └─ Recommendations
```

### With Pattern Learning

```
Context Analysis
  │
  ├─ Pattern Learning (always runs)
  ├─ Semantic Matching (if enabled)
  └─ LLM Analysis (if enabled and low confidence)
  
  Combine all and sort by confidence
```

### With Watch Mode

```bash
# Disable LLM in watch mode (run frequently)
cortex config set ai.use_llm_in_watch_mode false

# Watch mode will still use pattern + semantic matching
cortex watch
```

## Monitoring & Analytics

### View LLM Statistics

```bash
# Sessions using LLM
cortex stats --by source | grep llm

# Agents recommended by LLM
cortex stats --agent --source llm

# Cost tracking
cortex stats --cost --by week
```

### Cost Tracking

Your usage is tracked locally:

```
~/.local/share/cortex/
├── session_history.json
└── llm_analytics.json  # Cost and usage tracking
```

### Manual Audit

```bash
# Export usage data
cortex session export --format json > usage.json

# Analyze with your tools
jq '.[] | select(.llm_used) | {date, cost, agent}' usage.json
```

## When to Enable LLM

### Good Use Cases ✅

- Complex codebase with many potential agents
- Nuanced task that needs reasoning
- New project with limited history
- Unusual context patterns
- High-value work where quality > cost

### Not Necessary ❌

- Simple auth changes (pattern matching works well)
- Frequently repeated tasks
- Large-scale batch operations
- Cost-sensitive deployments

### Example Scenarios

| Scenario | LLM? | Why |
|----------|------|-----|
| Edit `auth.py` | ❌ No | Pattern matching is reliable |
| Novel multi-domain refactor | ✅ Yes | Needs reasoning |
| API endpoint update | ❌ No | Semantic matching works |
| Unusual hybrid feature | ✅ Yes | Context is ambiguous |
| Bulk file migrations | ❌ No | High volume, low ambiguity |

## FAQ

**Q: How does LLM compare to semantic matching?**

A: Semantic matching is faster and free but pattern-based. LLM actually reasons about your code. Typical workflow: use semantic first (50ms), use LLM only if uncertain (~2 seconds, $0.006).

**Q: Will it cost a lot?**

A: Not with good thresholds. With defaults, only ~10-20% of recommendations use LLM. That's ~$0.30/month for medium usage. Set budget limits to be safe.

**Q: Can I use a different LLM provider?**

A: Currently only Claude API is supported. Other providers can be added as contributions.

**Q: What if I hit rate limits?**

A: Increase `llm_threshold` to reduce API calls. Or disable for watch mode.

**Q: Does it learn from feedback?**

A: Not currently. Future versions will support active learning from your corrections.

**Q: Is my code sent to Anthropic?**

A: Only the context summary (file names, types, signals). Not the actual code. See privacy section below.

## Privacy & Data Handling

### What Gets Sent

- File names and paths
- File types (`.py`, `.ts`, etc.)
- Directory names
- Signal flags (has_auth, has_api, etc.)
- File counts and error counts
- Recent session history (agent names, outcomes)

### What Doesn't Get Sent

- Actual code content
- Commit messages or comments
- Variable/function names
- Personal data
- Secret/API keys

### Example Request

```
Files changed: 3
File types: .py
Directories: src/auth
Signals detected:
  - Tests: false
  - Auth: true
  - API: true
  - Frontend: false
  - Backend: true
  - Database: true
Errors: 0
Test failures: 0
Sample files: oauth.py, jwt.py, auth_handler.py
```

### Data Retention

- Your local sessions: Retained indefinitely (your machine)
- Claude's servers: Deleted after 30 days per Anthropic policy
- Your API usage: Visible in Anthropic console

## Configuration Reference

### Complete Config Example

```yaml
# ~/.claude/config.yml
ai:
  # Semantic matching
  semantic_enabled: true
  
  # LLM Intelligence
  use_llm: true                           # Enable LLM
  use_llm_in_watch_mode: false            # Disable in watch (frequent checks)
  
  # LLM Thresholds & Control
  llm_threshold: 0.5                      # Call LLM if confidence < 50%
  llm_budget_limit: 10.00                 # Monthly limit ($)
  llm_budget_period: monthly              # Reset period
  
  # Model & Performance
  llm_model: claude-sonnet-4-20250514    # Model to use
  llm_temperature: 0.3                    # Reasoning determinism (0.0-1.0)
  llm_max_tokens: 1024                    # Max response length
  
  # Auto-activation
  auto_activate: true                     # Auto-activate high-confidence
  auto_activate_threshold: 0.8            # Minimum confidence for auto-activate
```

## See Also

- [AI Intelligence Overview](../AI_INTELLIGENCE.md)
- [Semantic Matching Guide](../AI_IMPLEMENTATION_SUMMARY.md)
- [Anthropic API Docs](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Claude Models](https://docs.anthropic.com/claude/reference/models-overview)
