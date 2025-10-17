# Profile: incident-response
# Generated: 2024-09-22
# Description: Complete incident response workflow for production issues
# Tags: crisis,debugging,operations,production
# Auto-detect: docker-compose.yml + logs/, kubernetes + error patterns

# Agent tiers for resource management
CORE_AGENTS="incident-responder error-detective root-cause-analyst"
EXTENDED_AGENTS="devops-troubleshooter security-auditor performance-engineer"
SPECIALIST_AGENTS="network-engineer database-admin kubernetes-architect"

# Sequential activation dependencies
DEPENDENCIES="incident-responder->error-detective,root-cause-analyst->devops-troubleshooter"

# Mode and rules activation
MODES="Orchestration"
RULES="workflow-rules efficiency-rules"

# Resource settings
ACTIVATION_STRATEGY="tiered"  # core -> extended -> specialist
MAX_CONCURRENT_AGENTS="6"
PRIORITY="high"

# Workflow sequence
WORKFLOW="incident-responder,error-detective,root-cause-analyst,devops-troubleshooter"