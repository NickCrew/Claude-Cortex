# AI & LLM Intelligence Documentation

Complete documentation for the AI-powered intelligence system including semantic matching, LLM analysis, and agent recommendations.

## Quick Navigation

| Document | Purpose | Time |
|----------|---------|------|
| [LLM_QUICK_REFERENCE.md](LLM_QUICK_REFERENCE.md) | Copy-paste configs and commands | 2 min |
| [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md) | Complete guide with pricing, troubleshooting, advanced usage | 15-20 min |
| [../AI_INTELLIGENCE.md](../AI_INTELLIGENCE.md) | System overview and basic usage | 5-10 min |
| [../AI_IMPLEMENTATION_SUMMARY.md](../AI_IMPLEMENTATION_SUMMARY.md) | Technical implementation details | 10-15 min |

## For Different Use Cases

### 👤 New Users
Start here:
1. Read [../AI_INTELLIGENCE.md](../AI_INTELLIGENCE.md) (5 min) - understand the three levels
2. Follow Quick Start in [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md#quick-start) (2 min)
3. Use [LLM_QUICK_REFERENCE.md](LLM_QUICK_REFERENCE.md) for common tasks

### 💰 Cost-Conscious Users
1. Skip ahead to [Pricing & Costs](LLM_INTELLIGENCE_GUIDE.md#pricing--costs) section
2. Check [Cost Optimization](LLM_QUICK_REFERENCE.md#cost-optimization)
3. Set up budget limits and high threshold

### 🎯 Advanced Users
1. Read [Configuration](LLM_INTELLIGENCE_GUIDE.md#configuration) section
2. Explore [Advanced Usage](LLM_INTELLIGENCE_GUIDE.md#advanced-usage)
3. Review [API Reference](LLM_INTELLIGENCE_GUIDE.md#api-reference)

### 🔧 Developers
1. Start with [../AI_IMPLEMENTATION_SUMMARY.md](../AI_IMPLEMENTATION_SUMMARY.md)
2. Review [API Reference](LLM_INTELLIGENCE_GUIDE.md#api-reference) for integration
3. Check Python examples in [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md#python-integration)

### 🐛 Troubleshooting
Jump to [Troubleshooting](LLM_INTELLIGENCE_GUIDE.md#troubleshooting) in main guide, or use [LLM_QUICK_REFERENCE.md](LLM_QUICK_REFERENCE.md#troubleshooting)

## Document Overview

### LLM_QUICK_REFERENCE.md
**Best for**: Quick setup, common commands, fast reference

**Covers**:
- 2-minute setup
- Common configuration patterns
- Pricing quick facts
- Basic troubleshooting
- Command cheat sheet

**Length**: ~3KB, easy to scan

### LLM_INTELLIGENCE_GUIDE.md
**Best for**: Comprehensive understanding, deep configuration, advanced usage

**Covers**:
- Complete setup with all details
- How it works (architecture diagrams)
- Detailed configuration (20+ settings)
- Pricing breakdown with examples
- Understanding recommendations
- 8 best practices
- 7 troubleshooting scenarios
- 3 advanced usage patterns
- Privacy & data handling
- FAQ section
- Full configuration reference

**Length**: ~22KB, comprehensive reference

### AI_INTELLIGENCE.md
**Best for**: System overview, basic usage, feature exploration

**Covers**:
- Three intelligence levels
- Installation for each level
- Basic usage patterns
- Configuration overview
- Performance characteristics
- Examples
- Architecture
- API reference (basic)

**Length**: ~11KB, accessible overview

### AI_IMPLEMENTATION_SUMMARY.md
**Best for**: Technical details, implementation specifics

**Covers**:
- What was built
- Architecture breakdown
- Data flow diagrams
- Installation details
- Usage examples (code)
- Testing information
- Performance metrics
- Migration notes
- Conclusion

**Length**: ~14KB, technical focus

## Feature Comparison

| Feature | Quick Ref | Guide | Overview | Implementation |
|---------|-----------|-------|----------|-----------------|
| Setup instructions | ✅ Brief | ✅ Complete | ✅ Brief | ✅ Technical |
| Configuration | ✅ Common | ✅ All 20+ | ⚠️ Basic | ✅ Code |
| Pricing | ✅ Summary | ✅ Detailed | ✅ Basic | ✅ Metrics |
| Troubleshooting | ✅ Common | ✅ 7 scenarios | ⚠️ 1-2 | ❌ None |
| Advanced usage | ❌ No | ✅ Full | ❌ No | ✅ Code |
| Architecture | ✅ Diagram | ✅ Detailed | ✅ Summary | ✅ Deep |
| Examples | ⚠️ CLI | ✅ CLI + Python | ⚠️ CLI | ✅ Code |
| Privacy | ❌ No | ✅ Full section | ⚠️ Mention | ❌ No |

## Installation Paths

### Path 1: Quick Setup (5 minutes)
```
1. LLM_QUICK_REFERENCE.md → Setup section
2. Copy paste from Common Configuration
3. Start using!
```

### Path 2: Informed Setup (15 minutes)
```
1. LLM_INTELLIGENCE_GUIDE.md → How It Works
2. LLM_INTELLIGENCE_GUIDE.md → Pricing & Costs
3. LLM_QUICK_REFERENCE.md → Configuration
4. Start using with budget controls
```

### Path 3: Complete Understanding (30+ minutes)
```
1. AI_INTELLIGENCE.md → Full overview
2. LLM_INTELLIGENCE_GUIDE.md → Complete read
3. AI_IMPLEMENTATION_SUMMARY.md → Technical details
4. API Reference section for integration
```

## Configuration Examples

### Minimum (Conservative)
```bash
pip install cortex-py[llm]
export ANTHROPIC_API_KEY=sk-ant-...
cortex config set ai.use_llm true
cortex config set ai.llm_threshold 0.2  # Only use LLM if very uncertain
```

### Recommended (Balanced)
```bash
pip install cortex-py[llm]
export ANTHROPIC_API_KEY=sk-ant-...
cortex config set ai.use_llm true
cortex config set ai.llm_threshold 0.5    # Default
cortex config set ai.use_llm_in_watch_mode false  # Avoid watch surprises
cortex config set ai.llm_budget_limit 10.00  # Monthly budget
```

### Maximum (Quality-Focused)
```bash
pip install cortex-py[llm]
export ANTHROPIC_API_KEY=sk-ant-...
cortex config set ai.use_llm true
cortex config set ai.llm_threshold 0.8    # Use LLM more often
cortex config set ai.llm_model claude-opus-4-1  # Best quality
cortex config set ai.llm_temperature 0.0  # Deterministic
```

## Common Tasks

### I want to...

**...get started immediately** → [LLM_QUICK_REFERENCE.md](LLM_QUICK_REFERENCE.md#setup-2-minutes)

**...understand the pricing** → [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md#pricing--costs)

**...minimize costs** → [LLM_QUICK_REFERENCE.md](LLM_QUICK_REFERENCE.md#cost-optimization)

**...configure LLM** → [LLM_QUICK_REFERENCE.md](LLM_QUICK_REFERENCE.md#common-configuration)

**...fix an issue** → [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md#troubleshooting)

**...integrate in code** → [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md#api-reference)

**...understand what data is sent** → [LLM_INTELLIGENCE_GUIDE.md](LLM_INTELLIGENCE_GUIDE.md#privacy--data-handling)

**...disable for watch mode** → [LLM_QUICK_REFERENCE.md](LLM_QUICK_REFERENCE.md#common-configuration)

**...switch models** → [LLM_QUICK_REFERENCE.md](LLM_QUICK_REFERENCE.md#advanced-models)

## Key Concepts

### Three Intelligence Levels

1. **Level 1: Rule-Based** (Always)
   - Pattern matching and heuristics
   - Zero cost
   - Fast

2. **Level 2: Semantic Matching** (Optional)
   - FastEmbed embeddings
   - Zero API cost
   - 50ms queries

3. **Level 3: LLM Analysis** (Optional, Premium)
   - Claude API reasoning
   - ~$0.006 per analysis
   - 1-3 seconds

### Hybrid Strategy

```
New Context
  ↓
Try Level 2 (Semantic)
  ├─ Confidence > 0.5? → DONE
  └─ Confidence < 0.5? → Try Level 3 (LLM)
                         → DONE
```

### Cost Model

With smart thresholds:
- 80-90% of requests: Levels 1-2 (free)
- 10-20% of requests: Level 3 (LLM, ~$0.006 each)
- Average: ~$0.30/month for medium usage

## Frequently Asked Questions

**Q: Will this cost a lot?**
A: No. With defaults, only ~15% of recommendations use LLM. That's ~$0.30/month for 30 sessions/day.

**Q: What if I don't want to pay?**
A: Disable LLM: `cortex config set ai.use_llm false`. Semantic matching (free) still works.

**Q: Can I limit the cost?**
A: Yes! Set `llm_budget_limit` and increase `llm_threshold`.

**Q: Is my code sent to Anthropic?**
A: No. Only metadata (file names, types, signals). Never actual code.

**Q: Which model should I use?**
A: Sonnet (default) is best for most users. Haiku for cost, Opus for maximum quality.

See [FAQ section](LLM_INTELLIGENCE_GUIDE.md#faq) for more.

## Architecture Overview

```
Context Detection
    ↓
Semantic Matching (FastEmbed)
    ├─ Found good match (conf > 0.5)
    │   └─ Return recommendations
    └─ No good match (conf < 0.5)
        └─ LLM Analysis (Claude API)
            └─ Return recommendations
```

## Related Documentation

- [AI Intelligence Overview](../AI_INTELLIGENCE.md) - System overview
- [AI Implementation Details](../AI_IMPLEMENTATION_SUMMARY.md) - Technical architecture
- [Watch Mode Guide](../development/WATCH_MODE_GUIDE.md) - Real-time monitoring
- [Anthropic API Docs](https://docs.anthropic.com) - Claude API reference

## Support

- 🐛 Report bugs: [GitHub Issues](https://github.com/NickCrew/claude-cortex/issues)
- 💬 Questions: Check [FAQ](LLM_INTELLIGENCE_GUIDE.md#faq) or troubleshooting
- 📖 More help: See [Troubleshooting](LLM_INTELLIGENCE_GUIDE.md#troubleshooting) in main guide
- 🌐 API Help: [Anthropic Support](https://support.anthropic.com)

## Document Statistics

| Document | Lines | Words | Topics | Code Blocks |
|----------|-------|-------|--------|-------------|
| Quick Reference | 194 | 1,200 | 12 | 8 |
| LLM Guide | 650+ | 8,500+ | 20+ | 15+ |
| AI Intelligence | 430+ | 5,200+ | 15+ | 10+ |
| Implementation | 450+ | 5,800+ | 12+ | 8+ |

**Total AI Documentation**: ~1,700 lines, ~20,700 words

## Version History

- **v1.0** (2025-12-07): Initial comprehensive documentation
  - Quick reference guide
  - Complete LLM guide
  - Updated overview
  - Updated implementation guide
  - Full integration with main docs

## Contributing

Found an issue or want to improve docs? 
- Edit the relevant guide
- Test your changes
- Submit a pull request

## License

MIT - Same as cortex-plugin
