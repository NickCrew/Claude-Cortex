# LLM Intelligence Quick Reference

## Setup (2 minutes)

```bash
# 1. Install
pip install cortex-py[llm]

# 2. Add API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Enable
cortex config set ai.use_llm true
```

## Common Configuration

| Use Case | Command |
|----------|---------|
| **Conservative** (low cost) | `cortex config set ai.llm_threshold 0.2` |
| **Balanced** (default) | `cortex config set ai.llm_threshold 0.5` |
| **Aggressive** (high quality) | `cortex config set ai.llm_threshold 0.8` |
| **Low cost model** | `cortex config set ai.llm_model claude-haiku-3-5` |
| **Best quality** | `cortex config set ai.llm_model claude-opus-4-1` |
| **Disable watch mode** | `cortex config set ai.use_llm_in_watch_mode false` |
| **Set budget** | `cortex config set ai.llm_budget_limit 5.00` |

## Pricing Quick Facts

- **Haiku**: $0.00056 per analysis (cheapest)
- **Sonnet** (default): $0.006 per analysis (balanced)
- **Opus**: $0.0345 per analysis (best quality)

With defaults (~15% LLM call rate):
- 10 sessions/day ≈ $0.10/month
- 30 sessions/day ≈ $0.30/month
- 100 sessions/day ≈ $1.00/month

## Usage

```bash
# Get recommendations with LLM analysis
cortex ai recommend

# Check stats
cortex stats --by agent --source llm

# View last week's recommendations
cortex session list --since "7 days ago" | grep llm
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "LLM not available" | `pip install cortex-py[llm]` then restart |
| "Invalid API key" | Check https://console.anthropic.com/account/api-keys |
| "Rate limited" | Increase `llm_threshold` to 0.2 |
| "Model not found" | Use `claude-sonnet-4-20250514` (default valid model) |
| "High costs" | Increase `llm_threshold`, disable for watch mode |

## Configuration File

```yaml
# ~/.claude/config.yml
ai:
  use_llm: true
  llm_threshold: 0.5              # Call LLM if confidence < 50%
  llm_model: claude-sonnet-4-20250514
  llm_temperature: 0.3            # Lower = more deterministic
  llm_max_tokens: 1024
  use_llm_in_watch_mode: false    # Avoid surprise costs
  llm_budget_limit: 10.00         # Monthly limit
```

## What Gets Sent to API

✅ **Safe to send**:
- File names: `auth.py`, `api_routes.ts`
- File types: `.py`, `.ts`, `.rs`
- Directory names: `src/auth`, `api/handlers`
- Context signals: `has_auth: true`, `has_tests: false`
- File counts: `3 files changed`

❌ **Never sent**:
- Actual code content
- Variable/function names
- Commit messages
- Secrets or API keys

## Key Metrics

| Metric | Value |
|--------|-------|
| Response time | 1-3 seconds |
| Model | Claude Sonnet 4 (default) |
| Input tokens | ~500 typical |
| Output tokens | ~300 typical |
| Cost per call | ~$0.006 (Sonnet) |

## Advanced: Models

```bash
# Fastest & cheapest
cortex config set ai.llm_model claude-haiku-3-5

# Balanced (default)
cortex config set ai.llm_model claude-sonnet-4-20250514

# Best quality
cortex config set ai.llm_model claude-opus-4-1
```

## Advanced: Temperature (0.0-1.0)

```bash
# Very deterministic (recommended for agent selection)
cortex config set ai.llm_temperature 0.0

# Default (mostly deterministic)
cortex config set ai.llm_temperature 0.3

# Creative (not recommended for task selection)
cortex config set ai.llm_temperature 0.7
```

## Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY=sk-ant-...

# Optional
export CORTEX_LLM_MODEL=claude-sonnet-4-20250514
export CORTEX_LLM_THRESHOLD=0.5
export CORTEX_LLM_TEMPERATURE=0.3
export CORTEX_LLM_MAX_TOKENS=1024
```

## Recommendation Confidence Scale

| Score | Interpretation |
|-------|-----------------|
| 0.90-1.00 | Very certain |
| 0.70-0.90 | Quite confident |
| 0.50-0.70 | Moderately confident |
| 0.30-0.50 | Somewhat uncertain |
| 0.00-0.30 | Unlikely |

## When to Use LLM

### ✅ Use When:
- Complex multi-domain refactoring
- Unusual context patterns
- High-value work where quality > cost
- New projects with limited history

### ❌ Skip When:
- Simple auth changes (pattern matching sufficient)
- High-volume batch operations
- Cost-sensitive deployments
- Frequently repeated tasks

## Full Guide

📖 [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md) — Comprehensive documentation

## System Architecture

```
Session → Semantic Matching (free, 50ms)
            ↓
         Confidence > threshold (0.5)?
            ├─ YES → Return recommendations
            └─ NO → Call Claude API (1-3s, ~$0.006)
                     ↓
                  Return LLM recommendations
```

## Cost Optimization

**To minimize costs:**
1. Set `llm_threshold` high (0.2-0.3)
2. Disable in watch mode
3. Use Haiku model for cost-sensitive work
4. Set budget limit

**Result**: 80-90% of checks use free semantic matching, only 10-20% call API

## See Also

- Full guide: [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md)
- Overview: [../AI_INTELLIGENCE.md](../AI_INTELLIGENCE.md)
- Implementation: [../AI_IMPLEMENTATION_SUMMARY.md](../AI_IMPLEMENTATION_SUMMARY.md)
