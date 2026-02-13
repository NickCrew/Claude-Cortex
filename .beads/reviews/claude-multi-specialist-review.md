# Multi-Specialist Review Report

**Repo**: claude-cortex
**Branch**: main
**HEAD**: caf833907e47c4ecb97934ade42d42d022bf02ef
**Date**: 2026-02-08
**Specialists**: Security, Architecture, Configuration Consistency

---

## Summary

This changeset is a **housekeeping and reorganization** commit that:

1. **Moves** 5 Python scripts from `scripts/` to `bin/` (identical copies)
2. **Deletes** 2 hook scripts (`auto-reviewer.sh`, `review-gate.sh`) replaced by skill-based review
3. **Adds** 3 new hook scripts (`audit.sh`, `issue-generator.sh`, `post-edit-check.sh`)
4. **Adds** 2 new skills (`a10-brand/`, `vibe-security/`)
5. **Updates** 3 manpages (date bump + command list cleanup)
6. **Adds** new `bin/` directory with mixed-language executables
7. **Adds** `codex/skills/claude-multi-specialist-review/` (the skill invoking this review)

The primary risk is a **broken hooks.json** that still references deleted files. The rest is low-risk reorganization.

---

## Findings

### P0 - Critical

#### P0-1: hooks.json references deleted scripts (will cause runtime failures)

**File**: `hooks/hooks.json`
**Hunk**: `@@ -33,6 +33,10 @@` (unstaged diff lines 192-202)
**Lines**: 54, 58

The `UserPromptSubmit` section of hooks.json still references two deleted files:

```
Line 54: "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/auto-reviewer.sh\""
Line 58: "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/review-gate.sh\""
```

Both files are confirmed deleted (git status shows `D hooks/auto-reviewer.sh` and `D hooks/review-gate.sh`; verified absent on disk).

**Impact**: Every user prompt submission will trigger hook failures. Depending on the hook runner's error handling, this could:
- Silently fail (lost review functionality)
- Noisily fail (error spam on every prompt)
- Block execution (if hook runner treats failures as fatal)

**Fix**: Remove lines 50-61 from hooks.json (the `auto-reviewer.sh` and `review-gate.sh` entries), or replace with the new skill-based review mechanism.

---

### P1 - High

#### P1-1: Manpage documents commands that may not exist in CLI

**Files**: `docs/reference/cortex.1` (unstaged diff hunk `@@ -23,21 +23,12 @@` through `@@ -89,23 +53,17 @@`)

The cortex.1 manpage removes 13 commands: `mode`, `principles`, `prompts`, `init`, `profile`, `workflow`, `orchestrate`, `orch`, `config`, `start`, `claude`, `completion`, `docs`, `doctor`, `setup`. It also adds `review`.

**Risk**: If the underlying CLI still defines these commands (via `--help` or arg parser), the documentation diverges from implementation. Users who discover removed commands via `--help` won't find them in the manpage, and vice versa.

**Fix**: Verify the Rust CLI source no longer exposes these commands, or add a "Deprecated Commands" section to the manpage.

---

#### P1-2: cortex-workflow.1 has malformed roff syntax

**File**: `docs/reference/cortex-workflow.1` (unstaged diff hunk `@@ -1,42 +1,12 @@`)

The new DESCRIPTION section reads:
```
.B cortex-workflow
is Workflow management commands
```

The phrase "is Workflow management commands" is grammatically broken (should be "provides workflow management commands" or similar). Additionally, the entire COMMANDS section was removed, leaving only `-h, --help` in OPTIONS - making the manpage nearly content-free.

**Fix**: Correct the grammar and either restore relevant command documentation or add a note that commands are documented elsewhere.

---

#### P1-3: `bin/env` is an empty file

**File**: `bin/env` (untracked, 0 bytes)

An empty file named `env` in a `bin/` directory is confusing. It shadows the system `/usr/bin/env` if `bin/` is prepended to PATH. If this was meant to be a sourced environment configuration, it's incomplete.

**Fix**: Either populate with intended content or remove. If it's a placeholder, add a comment explaining its purpose.

---

### P2 - Medium

#### P2-1: `bin/` directory has no documentation or structure

**Files**: All files in `bin/` (untracked)

The new `bin/` directory contains 10 files across 4 languages:
- Python: `audit_skill.py`, `cortex_statusline.py`, `file_utils.py`, `skill_utils.py`
- Shell: `claude_wrapper.sh`, `committer`, `tx`
- TypeScript: `browser_tools.ts`, `docs_list.ts`
- Config: `env` (empty)

No README, no `__init__.py`, no package.json. The Python files moved from `scripts/` are identical copies (same line counts: audit_skill.py=743, file_utils.py=288, skill_utils.py=398). The docstrings still reference `scripts/` paths (e.g., `bin/audit_skill.py` line 8: `python scripts/audit_skill.py <skill-name>`).

**Impact**: Confusion about canonical file locations; stale documentation in docstrings.

**Fix**: Update docstrings in moved files to reference `bin/` paths. Consider adding a `bin/README.md`.

---

#### P2-2: New hooks not registered for all appropriate events

**File**: `hooks/hooks.json` lines 33-40

The new `post-edit-check.sh` is correctly added to `PostToolUse` with empty matcher (runs on all tool uses). However:
- `hooks/audit.sh` (Rust audit script) is NOT registered in hooks.json - it's a standalone script
- `hooks/issue-generator.sh` is NOT registered in hooks.json - it's a standalone script

This is likely intentional (they're manual-run tools, not auto-hooks), but the placement in `hooks/` alongside auto-hooks is misleading.

**Fix**: Consider moving standalone scripts to `bin/` or `scripts/` to distinguish them from auto-triggered hooks. Or add comments in hooks.json clarifying which files are auto-hooks vs standalone.

---

#### P2-3: Deleted scripts were utility libraries with external API dependencies

**Files**: Deleted `scripts/file_utils.py` (288 lines), `scripts/skill_utils.py` (398 lines)

These files contain Anthropic API client wrappers (`from anthropic import Anthropic`, `from anthropic.lib import files_from_dir`). They're now in `bin/` as identical copies. The deletion from `scripts/` is fine since copies exist in `bin/`, but verify no other code imports from `scripts.file_utils` or `scripts.skill_utils`.

**Verification**: Grep confirmed no imports from these modules exist elsewhere in the codebase.

---

#### P2-4: `post-edit-check.sh` uses `cd` without restoring directory

**File**: `hooks/post-edit-check.sh` lines 18, 38

The script uses `cd "$dir"` to find Cargo.toml/tsconfig.json directories but never restores the original working directory. Since this runs as a PostToolUse hook, it could change the working directory for subsequent operations if the hook runner doesn't isolate processes.

**Fix**: Use `pushd/popd` or run the check in a subshell: `(cd "$dir" && cargo check ...)`.

---

#### P2-5: `a10-brand` skill contains large binary assets

**Files**: `skills/a10-brand/assets/*.svg` (14 SVG files), `skills/a10-brand/assets/chart-reference.jsx` (400+ lines)

The A10 brand skill adds substantial binary/asset content to the repo. SVG files are text-based but can be large. This increases repo clone size permanently.

**Impact**: Minor - SVGs are typically small. But worth noting for repo hygiene.

---

## Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Hook failures on every prompt | High | Certain (P0-1) | Remove deleted hook references |
| User confusion from stale manpages | Medium | Likely | Sync manpages with CLI |
| Empty `bin/env` shadowing `/usr/bin/env` | Medium | Unlikely | Remove or populate |
| Working directory mutation from hook | Low | Possible | Subshell isolation |

---

## Recommended Fixes

### Must-fix before commit:
1. **Remove deleted hook references from hooks.json** (lines 50-61 in `UserPromptSubmit`)

### Should-fix:
2. Fix grammar in `cortex-workflow.1` DESCRIPTION section
3. Update docstrings in `bin/*.py` to reference new paths
4. Handle or remove empty `bin/env`
5. Wrap `cd` calls in `post-edit-check.sh` in subshells

### Consider:
6. Move standalone scripts (`audit.sh`, `issue-generator.sh`) out of `hooks/` directory
7. Verify CLI source matches manpage command list
8. Add brief README to `bin/`

---

## Suggested Tests

1. **Hook smoke test**: Run the Claude Code hook system and verify no errors from missing scripts:
   ```bash
   # Simulate UserPromptSubmit event and check for file-not-found errors
   CLAUDE_PLUGIN_ROOT=. bash hooks/auto-reviewer.sh 2>&1  # should fail
   ```

2. **post-edit-check.sh isolation test**: Verify working directory is preserved:
   ```bash
   cd /tmp && CLAUDE_FILE_PATH=/some/project/src/main.rs bash hooks/post-edit-check.sh && pwd
   # Should still be /tmp
   ```

3. **Manpage rendering test**:
   ```bash
   man -l docs/reference/cortex.1
   man -l docs/reference/cortex-workflow.1
   ```

---

## Methodology

Three specialist sub-agents were dispatched in parallel:
- **Security auditor**: Reviewed hooks for injection, traversal, and misconfiguration
- **Architecture reviewer**: Analyzed file reorganization, imports, and structural consistency
- **Configuration reviewer**: Verified hooks.json references against filesystem

Sub-agent outputs were synthesized with hallucination filtering. Two security findings (P0-1 about `eval` in audit.sh, P0-1 about command injection in post-edit-check.sh) were **rejected as hallucinated** - the agents described code that does not exist in the actual files. One architecture finding (broken Python imports in bin/) was also **rejected** - the files have no cross-imports. All findings in this report are verified against actual file contents.
