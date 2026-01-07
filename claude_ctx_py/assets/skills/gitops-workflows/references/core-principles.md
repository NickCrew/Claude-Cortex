# GitOps Core Principles

## OpenGitOps Standards

**1. Declarative**
- Entire desired system state expressed declaratively
- Infrastructure as Code (IaC) describes complete configuration
- No imperative scripts or manual interventions

**2. Versioned and Immutable**
- Canonical desired state stored in Git
- Full audit trail through Git history
- Ability to recreate entire system from repository

**3. Pulled Automatically**
- Software agents automatically pull desired state from Git
- No push-based deployments to production
- Clusters pull changes rather than CI pushing changes

**4. Continuously Reconciled**
- Agents ensure actual state matches desired state
- Automatic drift detection and correction
- Self-healing systems that recover from manual changes

## Benefits

**Operational advantages:**
- Complete deployment history through Git
- Fast rollback via Git revert
- Enhanced security (no cluster credentials in CI)
- Declarative disaster recovery
- Multi-cluster consistency
- Self-healing infrastructure

**Developer advantages:**
- Familiar Git workflows
- Pull request reviews for infrastructure changes
- Automated deployment pipeline
- Environment parity
- Clear change tracking
