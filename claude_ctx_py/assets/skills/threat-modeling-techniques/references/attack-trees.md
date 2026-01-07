# Attack Trees

**Definition:** Hierarchical diagrams showing attack paths from goals to methods.

## Structure

```
[Root: Attack Goal]
    |
    +-- [OR] Method 1
    |       |
    |       +-- [AND] Step 1.1
    |       +-- [AND] Step 1.2
    |
    +-- [OR] Method 2
            |
            +-- [AND] Step 2.1
```

**Key Concepts:**
- **OR nodes**: Alternative attack methods (any one succeeds)
- **AND nodes**: Required steps (all must succeed)
- **Leaf nodes**: Atomic attack actions
- **Root node**: Attacker's ultimate goal

## Example: Unauthorized Data Access

```
[Goal: Access Customer Database]
    |
    +-- [OR] Exploit SQL Injection
    |       |
    |       +-- [AND] Find vulnerable input field
    |       +-- [AND] Craft malicious SQL payload
    |       +-- [AND] Extract data from database
    |
    +-- [OR] Steal Admin Credentials
    |       |
    |       +-- [AND] Phishing attack on admin
    |       +-- [AND] Bypass 2FA (if enabled)
    |       +-- [AND] Login with stolen credentials
    |
    +-- [OR] Exploit Misconfigured Access Controls
            |
            +-- [AND] Enumerate API endpoints
            +-- [AND] Find unprotected endpoint
            +-- [AND] Access data without authentication
```

## Creating Attack Trees

### Process

1. **Define the attacker's goal** (root node)
   - Example: "Steal credit card data", "Disrupt service"

2. **Identify alternative attack methods** (OR nodes)
   - Different ways to achieve the goal
   - Each method is independent

3. **Break down each method into required steps** (AND nodes)
   - Sequential or parallel steps
   - All steps must succeed for method to work

4. **Assign attributes** to each node
   - Cost, skill level, detection likelihood, impact

5. **Analyze most likely attack paths**
   - Calculate aggregate attributes for paths
   - Identify easiest/cheapest/stealthiest paths

6. **Prioritize mitigations** for high-risk paths
   - Focus on high-probability, high-impact paths
   - Consider cost-effectiveness of mitigations

## Attributes to Track

### Cost
Resources required by attacker
- **Low**: Free tools, minimal time
- **Medium**: Commercial tools, days of effort
- **High**: Custom development, weeks of effort

### Skill Level
Technical expertise needed
- **Novice**: Script kiddie, pre-built tools
- **Intermediate**: Developer, moderate security knowledge
- **Expert**: Security professional, custom exploit development

### Detection Likelihood
Probability of being caught
- **Low**: Stealthy, hard to detect
- **Medium**: Detectable with monitoring
- **High**: Obvious, triggers immediate alerts

### Impact
Damage if successful
- **Low**: Minor inconvenience
- **Medium**: Data exposure, service degradation
- **High**: Major breach, complete compromise
- **Critical**: Catastrophic damage, regulatory violations

## Attack Tree Analysis

### Feasibility Scoring

For each attack path, calculate:

```
Path Feasibility = (1 / Cost) × (1 / Skill) × (1 / Detection)
```

Higher score = More likely attack vector

### Prioritization

Focus mitigations on paths with:
- **High feasibility**: Easy to execute
- **High impact**: Severe consequences
- **Low cost to mitigate**: Quick wins

## Example with Attributes

```
[Goal: Access Customer Database]
    |
    +-- [OR] SQL Injection
    |       Cost: Low | Skill: Intermediate | Detection: Medium | Impact: Critical
    |       |
    |       +-- [AND] Find vulnerable field (Cost: Low, Skill: Novice)
    |       +-- [AND] Craft payload (Cost: Low, Skill: Intermediate)
    |       +-- [AND] Extract data (Cost: Low, Skill: Intermediate)
    |
    +-- [OR] Steal Admin Credentials
    |       Cost: Medium | Skill: Intermediate | Detection: High | Impact: Critical
    |       |
    |       +-- [AND] Phishing (Cost: Low, Skill: Novice)
    |       +-- [AND] Bypass 2FA (Cost: High, Skill: Expert)
    |       +-- [AND] Login (Cost: Low, Skill: Novice)
    |
    +-- [OR] Misconfigured Access
            Cost: Low | Skill: Novice | Detection: Low | Impact: Critical
            |
            +-- [AND] Enumerate endpoints (Cost: Low, Skill: Novice)
            +-- [AND] Find unprotected endpoint (Cost: Low, Skill: Novice)
            +-- [AND] Access data (Cost: Low, Skill: Novice)
```

**Analysis:**
- **Highest Risk**: Misconfigured access (low cost, low skill, low detection)
- **Priority Mitigation**: Fix access controls, implement authentication
- **Secondary Risk**: SQL injection (common, well-known attack)
- **Lower Priority**: Credential theft (2FA makes it harder)

## Best Practices

- **Start broad, refine iteratively**: Begin with high-level goals, add detail
- **Include stakeholders**: Developers, security team, operations
- **Update regularly**: As system evolves, threats change
- **Document assumptions**: What security controls are assumed to exist?
- **Consider attacker profiles**: Nation-state vs. script kiddie vs. insider
- **Validate with penetration testing**: Do theoretical attacks work in practice?
