# Profile: modernization
# Generated: 2024-09-22
# Description: Legacy codebase modernization and technical debt reduction
# Tags: refactoring,architecture,modernization,technical-debt
# Auto-detect: old framework versions, deprecated dependencies, legacy patterns

# Agent tiers for resource management
CORE_AGENTS="legacy-modernizer architect-review refactoring-expert"
EXTENDED_AGENTS="system-architect security-auditor test-automator quality-engineer"
SPECIALIST_AGENTS="typescript-pro golang-pro rust-pro performance-engineer"

# Sequential activation dependencies
DEPENDENCIES="legacy-modernizer->architect-review,architect-review->refactoring-expert,refactoring-expert->test-automator"

# Mode and rules activation
MODES="Task_Management"
RULES="workflow-rules quality-rules"

# Resource settings
ACTIVATION_STRATEGY="tiered"
MAX_CONCURRENT_AGENTS="7"
PRIORITY="medium"

# Workflow sequence
WORKFLOW="legacy-modernizer,architect-review,refactoring-expert,security-auditor,test-automator,quality-engineer"