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

### architectural — Architectural Prose Claims

Verb-anchored prose claims about technology choices, integrations, or
architectural patterns. These are extracted by `extract_claims.py` using
heuristic regex patterns; AI verification confirms or denies each.

**Extraction patterns** (verb-anchored, post-filtered):

| Frame | Pattern | Captures |
|-------|---------|----------|
| `uses` | `uses\|using\|leverages X` | Capitalized target |
| `built` | `built/implemented/powered/deployed/hosted with/using/on/via X` | Capitalized target |
| `delegated` | `delegated/delegates to X` | Capitalized brand-like target |
| `via` | `via X` | Capitalized service/protocol name |
| `depends` | `depends on X` | Capitalized target |
| `follows` | `follows/implements/adopts the X pattern/architecture/model/approach` | Lowercase OK (saga, actor model) |
| `uses_pattern` | `uses/using/adopting (a\|the) X pattern/architecture/...` | Lowercase OK |

The `follows` and `uses_pattern` frames allow lowercase targets because real
architectural patterns are often lowercase ("actor model", "saga",
"publish-subscribe", "event sourcing"). Other frames require at least one
uppercase letter in the target to filter pronoun noise.

**Examples that match:**
- "Uses Redis for caching" → `Redis` via `uses`
- "Built with React and TypeScript" → `React`, `TypeScript` via `built`
- "Deployed on AWS Lambda" → `AWS Lambda` via `built`
- "Authentication is delegated to Auth0" → `Auth0` via `delegated`
- "We use a CQRS pattern for the order service" → `CQRS` via `uses`
- "follows the actor model" → `actor` via `follows`
- "We adopt the saga pattern" → `saga` via `follows`
- "Implements a publish-subscribe approach" → `publish-subscribe` via `follows`

**Examples that don't match (correctly):**
- "Use clear, descriptive commit messages" → no capitalized target → filtered
- "the system uses memory efficiently" → "memory" lowercase, not in
  pattern-suffix frame → filtered
- "Master Architecture" heading alone → no verb anchor → filtered (the old
  standalone `<X> pattern` rule was removed because it caught every heading)

**Verification:** AI agent (sonnet, per-docfile) reads dependency manifests
for `uses`/`built`/`depends`/`via` claims, scans for SDK imports or HTTP
integrations for `delegated` claims, and checks directory structure / class
names / code organization for `follows`/`uses_pattern` claims.

**Failure category:** `phantom_pattern` (when the claimed pattern has no
evidence in the codebase) or `wrong_integration` (when the named service
isn't actually integrated).

---

## AI-Discovered + Verified (Subagents)

These claims require understanding code semantics. The dependency and
behavioral verifiers both *discover* and *verify* in one agent pass — the
extraction script doesn't pre-extract them.

### dependency — Technology/Library Claims

Prose claims about what technologies the project uses, where the agent reads
manifests directly.

**Examples:**
- "Uses Redis for caching"
- "Built with React and TypeScript"
- "Deployed on AWS Lambda"

**Verification:** Haiku Explore agent reads dependency manifests
(`package.json`, `requirements.txt`, `go.mod`, etc.) and cross-references doc
claims. Stays on haiku because pattern-matching against manifests doesn't
benefit from sonnet's reasoning.

**Note:** This verifier overlaps with `architectural` (which extracts `uses X`
patterns regex-first and verifies per-docfile). The two agents complement: the
dependency verifier scans manifests and looks back to docs; the architectural
verifier starts from extracted claims and looks forward to code. Run both —
they catch different misses.

---

### behavioral — Code Behavior Claims

Assertions about what the code does, how it works, or what happens in specific
scenarios. *Not* regex-extracted — too free-form for reliable patterns. The
sonnet behavioral verifier reads each docfile, identifies behavioral claims,
and verifies them in one pass.

**Examples:**
- "The system retries failed requests 3 times"
- "Passwords are hashed with bcrypt before storage"
- "Requests are rate-limited to 100/minute"
- "The cache expires after 5 minutes"
- "The cache invalidates when the user logs out"

**Verification:** Sonnet `general-purpose` agent (per-docfile dispatch). Reads
the doc file, identifies behavioral claims, finds the relevant code via grep
or codanna, and checks whether the claimed behavior matches. Reports each
claim with status:
- **Confirmed**: Code does what the doc says
- **Contradicted**: Code does something different
- **Unverifiable**: Cannot locate relevant code (logs the behavioral claim and
  what was searched for, so a human can decide whether the claim is real but
  hidden, or vacuous)
- **Conditional**: True under some conditions, not others — note the
  conditions

**Why sonnet, not haiku:** behavioral verification often requires tracing
across multiple files (handler → middleware → config) and distinguishing
happy-path from error-path behavior. Haiku's `Explore` excerpt reads strain
on multi-hop traces; sonnet's `general-purpose` reads full files.

---

### example_code — Code Examples

Code blocks that demonstrate usage patterns.

**Examples:**
- Tutorial showing how to call an API
- Quick-start code snippet
- Configuration example

**Verification:** Sonnet `general-purpose` agent (per-docfile). Checks:
1. Do the function/method names exist?
2. Do the parameter names and types match current signatures?
3. Do the import paths resolve?
4. Would this code produce the described output?

Sonnet is required because signature comparison needs full-file reads of the
current implementation, not excerpts.
