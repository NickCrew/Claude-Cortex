# Claim Taxonomy

Complete classification of verifiable claims found in documentation.

## Mechanically Verifiable (Scripts)

These claims can be checked deterministically without AI.

### file_path — File Path References

Inline code that matches filesystem path patterns.

**Extraction pattern:** Backtick-wrapped text containing `/` and a file extension.

**Examples:**
- `` `src/auth/login.ts` `` → check `os.path.exists()`
- `` `scripts/deploy.sh` `` → check file exists
- `` `docs/architecture/overview.md` `` → check file exists

**Verification:** Resolve path relative to project root, then relative to the doc file's directory.

**False positive filters:**
- URL-like paths (`http://`, `https://`)
- Anchor-only references (`#section`)
- Abstract examples (`path/to/file`)

---

### command — Shell Commands

Commands in code blocks (with `$` prefix or shell language hint) and inline code
matching known command prefixes.

**Extraction pattern:** Lines starting with `$` in bash/sh blocks, or inline code
matching `npm|pip|python3?|cargo|go|make|docker|git|cortex|bd|claude ...`.

**Examples:**
- `` `npm run build` `` → check `package.json` scripts
- `` `python3 scripts/audit.py` `` → check script exists
- `$ cortex review` → check `cortex` binary on PATH or in `bin/`

**Verification:**
1. Extract base command (first word)
2. If path-like (`./scripts/foo.sh`): check file exists
3. If known system command: pass
4. Check `shutil.which()`
5. Check `package.json` scripts for `npm run X`
6. Check `bin/` directory

---

### code_ref — Code Symbol References

Function calls, class names, and method references in inline code.

**Extraction pattern:**
- Function calls: `word(...)` pattern
- Class references: `PascalCase` word
- Method references: `object.method` or `object.method()`

**Examples:**
- `` `authenticate()` `` → grep for `def authenticate` / `function authenticate`
- `` `UserService` `` → grep for `class UserService`
- `` `router.get()` `` → grep for `router` usage

**Verification:** `grep -r` the symbol name across source directories. A match in any
source file counts as verified.

**Limitations:** Cannot verify that the signature or behavior matches — only that the
symbol exists. Signature checking requires AI verification (Phase 2b).

---

### import — Import/Require Statements

Import declarations in code blocks.

**Extraction pattern:**
- `import X from 'Y'` (ES modules)
- `const X = require('Y')` (CommonJS)
- `from X import Y` (Python)
- `import X` (Python/Go/Java)

**Examples:**
- `import { Router } from 'express'` → check `express` in `package.json` dependencies
- `from pathlib import Path` → check Python stdlib
- `import "github.com/foo/bar"` → check `go.mod`

**Verification:**
1. Extract module name
2. If relative path: check file exists in project
3. If package name: check dependency manifests
4. If stdlib: check against known stdlib modules

---

### config — Configuration Keys

Environment variables and configuration option references.

**Extraction pattern:**
- `ALL_CAPS_UNDERSCORE` pattern (3+ chars)
- `${VAR_NAME}` references
- `KEY=value` assignments

**Examples:**
- `` `MAX_RETRIES` `` → grep source code for this key
- `` `DATABASE_URL` `` → grep for env var usage
- `` `NODE_ENV=production` `` → grep for `NODE_ENV`

**Verification:** Grep source code (excluding docs) for the config key. Found in source
means the option exists; not found means it may be phantom.

---

### url — External URLs

HTTP/HTTPS links in markdown.

**Extraction pattern:** Standard markdown `[text](https://...)` links.

**Verification:** HTTP HEAD request (opt-in only, `--check-urls` flag).
Not enabled by default because:
- Network dependency makes CI flaky
- Rate limiting causes false failures
- Slow on large doc sets

---

## AI-Verified (Subagents)

These claims require understanding code semantics and cannot be checked mechanically.

### dependency — Technology/Library Claims

Prose claims about what technologies the project uses.

**Examples:**
- "Uses Redis for caching"
- "Built with React and TypeScript"
- "Deployed on AWS Lambda"

**Verification:** AI agent reads dependency manifests, config files, and source code
to confirm or deny the claim.

---

### behavioral — Code Behavior Claims

Assertions about what the code does, how it works, or what happens in specific scenarios.

**Examples:**
- "The system retries failed requests 3 times"
- "Passwords are hashed with bcrypt before storage"
- "Requests are rate-limited to 100/minute"
- "The cache expires after 5 minutes"

**Verification:** AI agent finds the relevant code and checks whether the claimed
behavior matches the implementation. Reports:
- **Confirmed**: Code does what the doc says
- **Contradicted**: Code does something different
- **Unverifiable**: Cannot locate relevant code
- **Conditional**: True under some conditions, not others

---

### example_code — Code Examples

Code blocks that demonstrate usage patterns.

**Examples:**
- Tutorial showing how to call an API
- Quick-start code snippet
- Configuration example

**Verification:** AI agent checks:
1. Do the function/method names exist?
2. Do the parameter names and types match current signatures?
3. Do the import paths resolve?
4. Would this code produce the described output?
