# Testing & Quality Assurance Flags

Flags for test-driven development, coverage enforcement, and quality gates.

**Estimated tokens: ~170**

---

**--tdd / --test-first**
- Trigger: Feature implementation, bug fixes, refactoring
- Behavior: Force test-driven development workflow (write tests before code)
- Auto-enables: test-automator agent, validates test-first discipline
- Ensures: Red → Green → Refactor cycle is followed

**--coverage [80|90|95|100]**
- Trigger: Quality-critical projects, production code
- Behavior: Enforce minimum test coverage percentage
- Example: `--coverage 90` requires 90% test coverage before completion
- Fails: If coverage drops below threshold
- Reports: Coverage gaps with specific line numbers

**--mutation-test**
- Trigger: Critical business logic, high-stakes code
- Behavior: Enable mutation testing to verify test quality (not just coverage)
- Related: Ensures tests actually catch bugs, not just execute code
- Generates: Mutation score showing test effectiveness
- Use with: `--coverage` for comprehensive quality assurance
