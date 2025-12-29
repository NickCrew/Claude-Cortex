# Reference: budget

# /reasoning:budget - Thinking Budget Control

## Personas (Thinking Modes)
- **cost-optimizer**: Budget allocation, cost-benefit analysis, resource efficiency
- **performance-engineer**: Quality-cost trade-offs, reasoning effectiveness measurement
- **architect**: Task complexity assessment, appropriate budget sizing

## Delegation Protocol

**This command does NOT delegate** - Budget control is configuration setting.

**Why no delegation**:
- ❌ Instant configuration change
- ❌ Simple token budget setting
- ❌ Direct monitoring setup
- ❌ No execution required (just configuration)

**All work done directly**:
- Assess task complexity
- Set thinking token budget
- Enable usage monitoring if requested
- Track and report token consumption

**Note**: Personas guide budget decisions (optimizer for efficiency, performance for quality, architect for complexity).

## Tool Coordination
- **Direct configuration**: Token budget setting (direct)
- **Usage monitoring**: Token tracking (direct if --show-usage)
- **No delegation needed**: Pure configuration command

## Triggers
- Need to control reasoning depth and cost trade-offs
- Complex problems requiring extended thinking time
- Budget-conscious operations with quality requirements
- Performance optimization requiring variable reasoning depth

## Usage
```
/reasoning:budget [4000|10000|32000|128000] [--auto-adjust] [--show-usage]
```

## Behavioral Flow
1. **Assess**: Evaluate task complexity and budget requirements
2. **Configure**: Set internal thinking token budget for analysis
3. **Monitor**: Track token usage during reasoning process
4. **Optimize**: Suggest budget adjustments based on effectiveness
5. **Report**: Provide usage metrics and recommendations

Key behaviors:
- Fine-grained control over internal reasoning depth
- Cost optimization through explicit budget management
- Quality/cost trade-off visibility
- Automatic budget adjustment based on task complexity

## Budget Levels

### Standard (4,000 tokens)
- **Use case**: Routine development tasks, quick analysis
- **MCP servers**: Sequential (optional)
- **Thinking depth**: Systematic exploration with basic hypothesis testing
- **Cost**: ~$0.012 per request (input)
- **Equivalent**: `--think` / `/reasoning:adjust medium`
- **Best for**: Code reviews, simple refactoring, standard debugging

### Deep (10,000 tokens)
- **Use case**: Architectural decisions, complex refactoring
- **MCP servers**: Sequential + Context7
- **Thinking depth**: Deep exploration with trade-off analysis
- **Cost**: ~$0.030 per request (input)
- **Equivalent**: `--think-hard` / `/reasoning:adjust high`
- **Best for**: System design, dependency analysis, performance optimization

### Maximum (32,000 tokens)
- **Use case**: Critical system redesign, legacy modernization
- **MCP servers**: All available (Sequential, Context7, Codanna)
- **Thinking depth**: Exhaustive exploration with meta-analysis
- **Cost**: ~$0.096 per request (input)
- **Equivalent**: `--ultrathink` / `/reasoning:adjust ultra`
- **Best for**: Complex debugging, architectural transformation, security audits

### Extended (128,000 tokens) 🆕
- **Use case**: Extreme complexity requiring extended thinking time
- **MCP servers**: All available + skill composition
- **Thinking depth**: Maximum possible reasoning with exhaustive analysis
- **Cost**: ~$0.384 per request (input)
- **Equivalent**: Claude 3.7 Extended Thinking Mode
- **Best for**:
  - Multi-system integration challenges
  - Complex mathematical proofs or physics problems
  - Enterprise-scale architectural decisions
  - Security vulnerability chains with multiple attack vectors
  - Legacy system modernization with extensive dependencies

## Budget Control Options

### --auto-adjust
Automatically adjust budget based on task complexity signals:
- **Escalation triggers**: Circular dependencies, >100 files, >10 service boundaries
- **De-escalation triggers**: Simple patterns detected, confidence >0.9
- **Behavior**: Starts at requested budget, adjusts up/down as needed
- **Max escalation**: One level up (e.g., 10K → 32K, not 10K → 128K)

### --show-usage
Display real-time thinking budget consumption:
- Current tokens used vs allocated
- Estimated cost for current operation
- Budget efficiency score (quality per token)
- Recommendation for future similar tasks

## Cost Optimization Strategies

### Budget Selection Guide

**Budget Too Low Indicators:**
- Multiple solution attempts (>3) failing
- Confidence scores consistently <0.6
- Request for `/reasoning:adjust` escalation
- Circular reasoning or repeated analysis

**Budget Too High Indicators:**
- Task completed using <50% of allocated budget
- Solution found in first attempt with high confidence
- Minimal MCP server activation
- Simple, direct solution path

### Recommended Budgets by Task Type

**Code Analysis:**
- Quick scan: 4K
- Comprehensive: 10K
- Security audit: 32K
- Multi-system: 128K

**System Design:**
- Component design: 10K
- Service architecture: 32K
- Enterprise platform: 128K

**Debugging:**
- Simple bugs: 4K
- Complex bugs: 10K
- System-wide issues: 32K
- Production incidents: 128K

**Refactoring:**
- Function-level: 4K
- Module-level: 10K
- System-wide: 32K
- Legacy modernization: 128K

## Integration with Other Reasoning Controls

### Combined with /reasoning:adjust
```bash
# Set budget, then adjust depth mid-task
/reasoning:budget 32000
# ... task begins ...
/reasoning:adjust high --scope current
# Respects 32K budget but adjusts MCP activation
```

### Combined with --summary
```bash
# Extended thinking with brief output
--thinking-budget 128000 --summary brief
# Maximum reasoning, minimal output verbosity
```

### Combined with --reasoning-profile
```bash
# Extended security analysis
/analyze:code --thinking-budget 128000 --reasoning-profile security
# Maximum depth + domain specialization
```

## Tool Coordination
- **TodoWrite**: Budget monitoring and task tracking
- **Read/Grep**: Scope analysis for budget estimation
- **MCP Servers**: Activated based on budget level
- **Skill System**: Extended mode enables full skill composition

## Key Patterns
- **Budget Ladder**: 4K → 10K → 32K → 128K (progressive escalation)
- **Cost Awareness**: Show cost implications before extended thinking
- **Quality Metrics**: Track reasoning effectiveness per budget level
- **Auto-Optimization**: Learn optimal budgets for task patterns

## Examples

### Standard Development Task
```bash
/reasoning:budget 4000
# Set 4K budget for routine code review
# Cost-effective for simple analysis
```

### Complex Architectural Decision
```bash
/reasoning:budget 32000 --auto-adjust
# Start with 32K, allow escalation to 128K if needed
# Balances cost with quality for uncertain complexity
```

### Extended Thinking for Critical Issue
```bash
/reasoning:budget 128000 --show-usage
# Maximum depth for production incident investigation
# Monitor token usage and cost in real-time
```

### Budget-Conscious Analysis
```bash
/reasoning:budget 10000
/analyze:code src/auth --reasoning-profile security
# Deep analysis within controlled budget
# Security profile + 10K tokens = thorough but not excessive
```

## Boundaries

**Will:**
- Set explicit token budget for internal reasoning
- Monitor and report budget usage and efficiency
- Suggest optimal budgets based on task characteristics
- Enable extended thinking mode (128K) for extreme complexity

**Will Not:**
- Exceed budget without explicit --auto-adjust permission
- Charge for unused allocated budget (actual usage only)
- Guarantee quality solely based on budget (task-dependent)
- Replace manual depth adjustment (/reasoning:adjust)

## Pricing Reference

**Claude 3.7 Sonnet Pricing:**
- Input: $3 per million tokens
- Output: $15 per million tokens

**Extended Thinking Cost Examples:**
- 4K thinking → ~$0.012 input
- 10K thinking → ~$0.030 input
- 32K thinking → ~$0.096 input
- 128K thinking → ~$0.384 input

**Note:** Output tokens charged separately based on actual response length. Extended thinking generates more output but also higher quality responses.

**Cost Comparison:**
- Claude 3.7 (128K): $0.384 per request
- OpenAI o1 (128K): $1.920 per request (5x more expensive)

## Related Commands

- `/reasoning:adjust` - Runtime depth control (MCP activation)
- `/reasoning:metrics` - Track reasoning effectiveness
- `/analyze:code --reasoning-profile` - Domain-specific optimization
