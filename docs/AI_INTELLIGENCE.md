# AI Intelligence Features

cortex includes an intelligent agent recommendation system that learns from your usage patterns and makes smart suggestions about which agents to activate.

## Overview

The intelligence system uses a **hybrid approach** combining three techniques:

1. **Semantic Matching** (optional) - Uses embeddings to find semantically similar past sessions
2. **Pattern Learning** - Learns from frequency of agent usage in similar contexts
3. **Rule-Based Heuristics** - Applies domain knowledge for reliable recommendations

## Intelligence Levels

### Level 1: Rule-Based (Always Available)

The base level provides intelligent recommendations based on detected context signals:

- **Security Auditor**: Auto-activates when auth code is detected
- **Test Automator**: Auto-activates when test failures occur
- **Quality Engineer**: Auto-activates for any non-empty changeset
- **Code Reviewer**: Auto-activates for any non-empty changeset
- **Performance Engineer**: Auto-activates for database/API or perf-sensitive changes
- **API Documenter**: Recommends for API changes

**Multi-review bundles** (can trigger 5+ reviewers at once):

- **TypeScript** → `typescript-pro`
- **React / JSX / TSX** → `react-specialist`
- **User-facing UI** → `ui-ux-designer`
- **Database / SQL** → `database-optimizer`, `sql-pro`
- **Cross-cutting architecture** → `architect-review`

**Installation**: Built-in, no additional dependencies

### Level 2: Semantic Matching (Recommended)

Adds semantic similarity matching using FastEmbed to find similar past sessions:

```bash
# Install semantic intelligence
pip install cortex-py[ai]
```

**Benefits**:

- Understands that `auth.py` ≈ `login.ts` ≈ `oauth_handler.go`
- Learns from actual usage patterns
- Fast (~50ms per query)
- Works offline
- No API costs

**How it works**:

1. Records embeddings of successful sessions
2. When new context appears, finds semantically similar past sessions
3. Recommends agents that worked in those similar contexts

### Level 3: LLM-Powered (Premium, Opt-In)

Uses Claude API for actual reasoning about context:

```bash
# Install LLM intelligence
pip install cortex-py[llm]

# Enable LLM recommendations (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=your_key_here
cortex config set ai.use_llm true
```

**Benefits**:

- Actually reasons about context (not just pattern matching)
- Understands nuance ("this is a refactoring task, not new feature")
- Can explain recommendations
- Considers agent combinations

**Costs**:

- ~$0.003-0.01 per recommendation
- Only called when semantic confidence is low (<0.5)
- Can be disabled for watch mode

## Usage

### Basic Usage (Automatic)

Intelligence features work automatically in the background:

```bash
# Start working - intelligence observes
git status
# Intelligence detects: "auth changes, 8 files, high complexity"

# Get recommendations
cortex ai recommend
# ✓ security-auditor (95% confidence) - Auth code detected
# ✓ quality-engineer (85% confidence) - Changes detected
# ✓ code-reviewer (75% confidence) - Changes detected
# ✓ typescript-pro (85% confidence) - TypeScript changes detected
# ✓ react-specialist (80% confidence) - React/UI changes detected
```

### Recording Success

The system learns from successful sessions:

```bash
# Work on a feature
cortex agent activate api-documenter code-reviewer

# ... make changes ...

# Record success (helps intelligence learn)
cortex ai record-success --outcome "API docs updated successfully"
```

### Configuration

```bash
# Enable/disable semantic matching
cortex config set ai.semantic_enabled true

# Enable/disable LLM recommendations
cortex config set ai.use_llm false

# Set LLM confidence threshold (only call LLM if semantic < threshold)
cortex config set ai.llm_threshold 0.5

# Select model (affects quality/cost)
cortex config set ai.llm_model claude-sonnet-4-20250514

# Control determinism
cortex config set ai.llm_temperature 0.3

# Limit response size
cortex config set ai.llm_max_tokens 1024

# Disable LLM in watch mode
cortex config set ai.use_llm_in_watch_mode false

# Auto-activate high-confidence recommendations
cortex config set ai.auto_activate true

# Set auto-activation threshold
cortex config set ai.auto_activate_threshold 0.8
```

See also: guides/ai/LLM_INTELLIGENCE_GUIDE.md#configuration

## How It Works

### Hybrid Recommendation Flow

```
Current Context
     │
     ▼
┌─────────────────────────────────────────┐
│ 1. Semantic Matching (if available)    │
│    - Find similar past sessions         │
│    - Weight agents by similarity        │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ 2. Pattern Matching                     │
│    - Look for exact context matches     │
│    - Recommend by frequency             │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ 3. Rule-Based Heuristics                │
│    - Apply domain knowledge             │
│    - High-confidence fallback           │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ 4. Deduplicate & Sort                   │
│    - Keep highest confidence            │
│    - Sort by confidence                 │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ 5. LLM Analysis (if needed)             │
│    - Only if confidence < threshold     │
│    - Only if user opted in              │
└─────────────────────────────────────────┘
     │
     ▼
Agent Recommendations
```

### Context Detection

The system automatically detects context from:

- **Files changed**: Type, location, names
- **Signals**: Auth, API, database, tests, frontend, backend
- **Activity**: Errors, test failures, build failures
- **History**: Past sessions with similar characteristics

### Learning Process

1. **Record**: When you complete a session, record:
   - Context (files, signals, activity)
   - Agents activated
   - Duration and outcome

2. **Embed** (if semantic enabled): Create semantic embedding of:
   - File paths (carry strong signals)
   - Domain keywords (auth, api, database, etc.)
   - Agents used (strong similarity signal)

3. **Match**: When new context appears:
   - Find semantically similar past sessions (fast)
   - Find exact pattern matches (reliable)
   - Apply rule-based heuristics (fallback)

4. **Recommend**: Combine all signals:
   - Semantic similarity score
   - Pattern frequency
   - Rule-based confidence
   - Deduplicate, keeping highest confidence

## Performance

### Semantic Matching Performance

- **Model**: BAAI/bge-small-en-v1.5 (33MB)
- **Embedding time**: ~50ms per session
- **Query time**: ~50ms for 1000 cached sessions
- **Memory**: ~1KB per cached session
- **Accuracy**: 0.82 on MTEB benchmark

### LLM Performance

- **Model**: Claude Sonnet 4
- **Latency**: 1-3 seconds per call
- **Cost**: ~$0.003-0.01 per recommendation
- **Usage**: Only when semantic confidence < 0.5

## Examples

### Example 1: Auth Feature Development

```bash
# Edit auth files
$ vim src/auth/oauth.py src/auth/jwt.py

# Get recommendations
$ cortex ai recommend

Recommendations:
┌───────────────────┬────────────┬─────────────────────────────────────┐
│ Agent             │ Confidence │ Reason                              │
├───────────────────┼────────────┼─────────────────────────────────────┤
│ security-auditor  │ 95%        │ Auth code detected (auto-activated) │
│ code-reviewer     │ 85%        │ Used in similar sessions (semantic) │
│ test-automator    │ 75%        │ Used in 3/4 auth sessions (pattern) │
└───────────────────┴────────────┴─────────────────────────────────────┘

Auto-activated: security-auditor
```

### Example 2: API Development

```bash
# Edit API files
$ vim api/routes.ts api/handlers.ts

# System learns from history
# Previously: API changes → api-documenter + code-reviewer

$ cortex ai recommend

Recommendations:
┌──────────────────┬────────────┬──────────────────────────────────┐
│ Agent            │ Confidence │ Reason                           │
├──────────────────┼────────────┼──────────────────────────────────┤
│ api-documenter   │ 90%        │ Used in 9/10 API sessions        │
│ code-reviewer    │ 85%        │ Used in 8/10 API sessions        │
│ test-automator   │ 70%        │ Used in semantically similar     │
└──────────────────┴────────────┴──────────────────────────────────┘
```

## Best Practices

### 1. Record Successes

Help the system learn by recording successful sessions:

```bash
cortex ai record-success --outcome "Feature complete, tests passing"
```

### 2. Use Semantic Matching

Install FastEmbed for much better recommendations:

```bash
pip install cortex-py[ai]
```

### 3. Start Conservative with LLM

Only enable LLM recommendations if semantic matching isn't enough:

```bash
# High threshold = rare LLM calls
cortex config set ai.llm_threshold 0.3

# Low threshold = frequent LLM calls (costs more)
cortex config set ai.llm_threshold 0.7
```

### 4. Review Auto-Activations

Check what gets auto-activated:

```bash
# See what would be auto-activated
cortex ai recommend

# Adjust threshold if too aggressive (future config)
cortex config set ai.auto_activate_threshold 0.9
```

## Troubleshooting

### "Semantic matching not available"

Install FastEmbed:

```bash
pip install cortex-py[ai]
```

### "LLM recommendations not available"

Install Anthropic SDK:

```bash
pip install cortex-py[llm]
export ANTHROPIC_API_KEY=your_key
```

More help: guides/ai/LLM_INTELLIGENCE_GUIDE.md#troubleshooting

### "No recommendations"

The system needs history to learn from:

1. Work on a few sessions
2. Record successes with `cortex session complete`
3. Give it time to build up patterns

### "Wrong agents recommended"

1. Review recorded sessions: `cortex session list`
2. Clear bad sessions: `cortex session clear --before "2024-01-01"`
3. Record correct patterns going forward

## Architecture

### Components

```
intelligence/
├── base.py          # Core pattern learning, rule-based heuristics
├── semantic.py      # Semantic matching with FastEmbed (optional)
│                    # LLM intelligence with Claude API (optional)
└── __init__.py      # Graceful degradation, availability flags
```

### Data Storage

```
~/.local/share/cortex/
├── session_history.json     # Pattern learning data
└── semantic_cache/
    └── session_embeddings.jsonl  # Semantic embeddings
```

## API Reference

### PatternLearner

```python
from claude_ctx_py.intelligence import PatternLearner, SessionContext

# Initialize
learner = PatternLearner(
    history_file=Path("session_history.json"),
    enable_semantic=True  # Use semantic matching
)

# Record success
learner.record_success(
    context=session_context,
    agents_used=["code-reviewer", "test-automator"],
    duration=1800,  # 30 minutes
    outcome="success"
)

# Get recommendations
recommendations = learner.predict_agents(session_context)
for rec in recommendations:
    print(f"{rec.agent_name}: {rec.confidence:.0%} - {rec.reason}")
```

### SemanticMatcher

```python
from claude_ctx_py.intelligence import SemanticMatcher

# Initialize
matcher = SemanticMatcher(cache_dir=Path("semantic_cache"))

# Add session
matcher.add_session({
    "files": ["auth.py", "login.py"],
    "context": {"has_auth": True},
    "agents": ["security-auditor"]
})

# Find similar
similar = matcher.find_similar(
    current_context={"files": ["oauth.py"], "context": {"has_auth": True}},
    top_k=5,
    min_similarity=0.6
)
```

## Future Enhancements

- [ ] Multi-model ensemble (combine multiple embedding models)
- [ ] Temporal patterns (time-of-day, day-of-week agent usage)
- [ ] User-specific learning (different patterns per developer)
- [ ] Active learning (ask for feedback on recommendations)
- [ ] Negative examples (learn from bad recommendations)
- [ ] Agent combination suggestions (which agents work well together)
- [ ] Workflow prediction (predict entire agent sequences)

## Additional Resources

Guides:

- guides/ai/LLM_INTELLIGENCE_GUIDE.md — Detailed LLM configuration and usage
- AI_IMPLEMENTATION_SUMMARY.md — Technical implementation details

External:

- FastEmbed: <https://github.com/qdrant/fastembed>
- BGE Embeddings: <https://huggingface.co/BAAI/bge-small-en-v1.5>
- Claude API: <https://docs.anthropic.com/claude/reference/getting-started-with-the-api>
- Claude Models: <https://docs.anthropic.com/claude/reference/models-overview>
- Pricing: <https://www.anthropic.com/pricing/claude>
