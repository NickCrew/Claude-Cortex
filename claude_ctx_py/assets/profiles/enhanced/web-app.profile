# Profile: web-app
# Generated: 2024-09-22
# Description: Full-stack web application development with modern practices
# Tags: frontend,backend,security,testing,web
# Auto-detect: package.json + [react,vue,angular,next], src/components/

# Agent tiers for resource management
CORE_AGENTS="system-architect security-auditor test-automator"
EXTENDED_AGENTS="ui-ux-designer backend-architect performance-engineer javascript-pro"
SPECIALIST_AGENTS="typescript-pro sql-pro api-documenter"

# Sequential activation dependencies
DEPENDENCIES="system-architect->backend-architect,security-auditor->test-automator"

# Mode and rules activation
MODES="Task_Management"
RULES="workflow-rules quality-rules"

# Resource settings
ACTIVATION_STRATEGY="tiered"
MAX_CONCURRENT_AGENTS="8"
PRIORITY="medium"

# Workflow sequence
WORKFLOW="requirements-analyst,system-architect,ui-ux-designer,backend-architect,security-auditor,test-automator"