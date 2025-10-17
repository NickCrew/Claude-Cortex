# Profile: data-pipeline
# Generated: 2024-09-22
# Description: Data engineering, analytics, and ML pipeline development
# Tags: data,analytics,ml,pipeline,etl
# Auto-detect: requirements.txt + [pandas,spark,airflow], .sql files, jupyter notebooks

# Agent tiers for resource management
CORE_AGENTS="data-engineer data-scientist sql-pro"
EXTENDED_AGENTS="ml-engineer mlops-engineer database-optimizer python-pro"
SPECIALIST_AGENTS="ai-engineer database-admin cloud-architect performance-engineer"

# Sequential activation dependencies
DEPENDENCIES="data-engineer->sql-pro,data-scientist->ml-engineer,ml-engineer->mlops-engineer"

# Mode and rules activation
MODES="Task_Management"
RULES="workflow-rules quality-rules"

# Resource settings
ACTIVATION_STRATEGY="tiered"
MAX_CONCURRENT_AGENTS="7"
PRIORITY="medium"

# Workflow sequence
WORKFLOW="requirements-analyst,data-engineer,sql-pro,data-scientist,ml-engineer,mlops-engineer"