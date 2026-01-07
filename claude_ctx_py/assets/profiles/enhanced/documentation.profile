# Profile: documentation
# Generated: 2025-10-13
# Description: Technical documentation, API docs, architecture guides, and knowledge base creation
# Tags: documentation,technical-writing,api-docs,architecture,knowledge-base
# Auto-detect: README.md + docs/, *.md files > 10, confluence/, wiki/

# Agent tiers for resource management
CORE_AGENTS="docs-architect api-documenter system-architect"
EXTENDED_AGENTS="code-reviewer typescript-pro python-pro"
SPECIALIST_AGENTS="database-optimizer security-auditor"

# Sequential activation dependencies
DEPENDENCIES="system-architect->docs-architect,code-reviewer->api-documenter"

# Mode and rules activation
MODES="Task_Management"
RULES="workflow-rules quality-rules"

# Resource settings
ACTIVATION_STRATEGY="tiered"
MAX_CONCURRENT_AGENTS="6"
PRIORITY="medium"

# Workflow sequence
WORKFLOW="system-architect,docs-architect,code-reviewer,api-documenter"
