  # Workflow Rules

  ## Task Pattern & Planning
  - **Task Pattern**: Understand → Plan → TodoWrite(3+ tasks) → Execute → Track → Validate
  - **Quality Checks**: Run lint/typecheck before marking tasks complete
  - **Evidence-Based**: All claims must be verifiable

  ## Execution Efficiency (canonical)
  - **Best Tool Selection**: Use the strongest available tool for the task; default to AGENTS tooling guidance.
  - **Parallel Everything**: Run independent operations in parallel; prefer Task agents for multi-step or multi-file work.
  - **Batch Operations**: Use MultiEdit for multi-file edits instead of serial single edits.
  - **Agent Delegation**: Delegate complex workstreams to Task agents when visibility or concurrency is needed.

  ## Workspace Hygiene
  - **Clean After Operations**: Remove temporary files when done.
  - **No Artifact Pollution**: Delete build artifacts, logs, and debugging outputs.
  - **Professional Workspace**: Keep project structure tidy.

  ## Git Workflow
  - **Always Check Status First**: Start every session with `git status` and `git branch`
  - **Feature Branches Only**: Create feature branches for ALL work, never work on main/master
  - **Incremental Commits**: Commit frequently with meaningful messages
  - **Verify Before Commit**: Always `git diff` to review changes before staging
  - **Critical**: See @rules/git-rules.md for commit standards and AI attribution PROHIBITION

  ## Implementation Completeness
  - **No Partial Features**: If you start implementing, you MUST complete to working state
  - **No TODO Comments**: Never leave TODO for core functionality
  - **Real Code Only**: All generated code must be production-ready

