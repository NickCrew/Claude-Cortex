# Learning & Education Flags

Flags for educational mode, explanations, and knowledge transfer.

**Estimated tokens: ~160**

---

**--teach-me / --explain**
- Trigger: Learning new concepts, onboarding, code reviews
- Behavior: Educational mode with detailed explanations and examples
- Auto-enables: Step-by-step breakdowns, "why" explanations, alternatives shown
- Includes: Code comments explaining decisions, links to documentation
- Format: Progressive disclosure from simple to complex

**--eli5 / --beginner**
- Trigger: Complex topics, new team members, documentation
- Behavior: Explain like I'm five - simplified explanations without jargon
- Related: Pair with --teach-me for maximum clarity
- Avoids: Technical terminology, assumes no prior knowledge
- Uses: Analogies, simple examples, visual metaphors

**--show-alternatives**
- Trigger: Architectural decisions, multiple valid approaches
- Behavior: Present 2-3 solution approaches with pros/cons analysis
- Auto-enables: Comparison tables, trade-off analysis
- Includes: Performance implications, complexity scores, maintainability ratings
- Format: Side-by-side comparison with recommendations

**--best-practices**
- Trigger: Production code, team projects, maintainability focus
- Behavior: Enforce industry best practices and design patterns
- Auto-enables: Code review with best practice validation
- Checks: SOLID principles, design patterns, security practices
- References: Industry standards, style guides, documentation
