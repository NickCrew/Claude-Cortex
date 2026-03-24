# Coverage Model

Defines what "complete documentation" means for different doc types and audiences.
Use this reference to calibrate expectations during Phase 1 inventory building.

---

## Coverage Expectations by Doc Type

### Reference Documentation

A reference page is complete when it covers:

- [ ] Every public parameter, flag, option, or config key
- [ ] Default values for all optional parameters
- [ ] Type/format constraints (string, integer, enum values)
- [ ] At least one example per parameter showing its effect
- [ ] Error conditions and what triggers them
- [ ] Related/see-also links to guides and tutorials that use this feature
- [ ] Version or changelog note if behavior changed recently

**Minimum bar:** Every public API surface has a reference entry. A missing entry is a P0-P1 gap.

### Tutorials

A tutorial is complete when:

- [ ] Prerequisites are stated explicitly (tools, versions, prior knowledge)
- [ ] Every step is numbered and actionable
- [ ] Expected output is shown for key steps
- [ ] The reader achieves a tangible result by the end
- [ ] Common errors at each step have troubleshooting guidance
- [ ] Estimated completion time is stated
- [ ] Next steps or further reading are linked

**Minimum bar:** A new user can follow the tutorial from start to finish without external help.
A tutorial that can't be completed is a P0 gap.

### Guides (How-To)

A guide is complete when:

- [ ] The problem or goal is stated clearly at the top
- [ ] Prerequisites are listed
- [ ] The solution is presented with enough context to adapt
- [ ] Edge cases or variations are noted
- [ ] The guide links to reference docs for parameters it uses
- [ ] Expected result is described

**Minimum bar:** A user with the stated prerequisites can accomplish the goal.

### Explanations

An explanation is complete when:

- [ ] The concept or system being explained is named and scoped
- [ ] "Why" is addressed, not just "what"
- [ ] Diagrams or visualizations support complex relationships
- [ ] Trade-offs and alternatives are acknowledged
- [ ] Links to reference and guides provide the "how"

**Minimum bar:** A reader understands the design rationale, not just the mechanics.

### README

A README is complete when:

- [ ] One-line description of what the project does
- [ ] Installation instructions (or link to them)
- [ ] Basic usage example
- [ ] Link to full documentation
- [ ] License information
- [ ] How to contribute (or link to CONTRIBUTING.md)

---

## Coverage Expectations by Audience

### New Users

Must have:
- Installation guide (P0 if missing)
- Quick start / first-use tutorial (P0 if missing)
- Core concepts explanation (P1 if missing)
- Troubleshooting for common first-run errors (P1 if missing)

### Daily Users

Must have:
- Complete reference for all features they interact with (P1 if missing)
- Guides for common workflows (P2 if missing)
- Changelog or what's new for upgrades (P2 if missing)

### Contributors / Developers

Must have:
- Development setup guide (P1 if missing)
- Architecture overview (P2 if missing)
- Testing guide (P2 if missing)
- Contribution guidelines (P2 if missing)

### Operators

Must have:
- Deployment guide (P1 if missing)
- Configuration reference with all env vars and defaults (P1 if missing)
- Monitoring and observability guide (P2 if missing)
- Backup and recovery procedures (P2 if missing)
- Upgrade and migration guides (P2 if missing)

---

## Determining "Should Document" vs. "Correctly Undocumented"

Not everything needs docs. Skip inventory items that are:

- **Internal implementation details** — private functions, internal data structures
- **Deprecated and scheduled for removal** — unless the migration path is undocumented
- **Generated from source** — if auto-generated docs are complete and accurate
- **Third-party documentation** — link to upstream docs, don't duplicate
- **Self-documenting** — trivially obvious from names and types (use judgment)

When in doubt, check: "Would a real user ever search for this?" If yes, it should be
in the inventory. If no, skip it.
