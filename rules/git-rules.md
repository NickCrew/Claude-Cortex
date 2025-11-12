# Git Commit Rules

## 🔴 CRITICAL: AI Authorship FORBIDDEN

### NEVER Sign Commits as AI/Claude
**This is a ZERO-TOLERANCE rule**:
- ❌ NEVER use `Co-Authored-By: Claude <noreply@anthropic.com>`
- ❌ NEVER sign commits with AI attribution
- ❌ NEVER claim authorship as "Claude" or any AI identity
- ❌ NEVER add "Generated with Claude Code" unless the USER explicitly requests it
- ✅ ONLY commit in the user's name with their configured git identity
- ✅ ONLY add attribution if user explicitly requests with clear confirmation

**Rationale**: Commits represent legal authorship. AI cannot hold copyright. All code modifications are authored by the human user, with AI as a tool.

**Enforcement**: Before ANY git commit command:
1. Check commit message does NOT contain AI attribution
2. Verify no Co-Authored-By lines reference AI/Claude
3. Confirm user's git identity will be used
4. If ANY AI attribution detected → STOP and remove it

## Conventional Commits Standard

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types (REQUIRED)
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting (no logic change)
- `refactor`: Code restructuring (no feature/fix)
- `perf`: Performance improvement
- `test`: Test additions/changes
- `build`: Build system/dependency changes
- `ci`: CI/CD configuration changes
- `chore`: Maintenance tasks
- `revert`: Revert previous commit

### Scope (OPTIONAL)
Specify component affected: `(api)`, `(ui)`, `(auth)`, `(core)`, etc.

Examples:
- `feat(api): add user pagination endpoint`
- `fix(auth): resolve token expiration bug`
- `refactor(core): extract agent parsing logic`

## Atomic Commits

### One Logical Change Per Commit
✅ **GOOD**:
- Single bug fix with tests
- One feature implementation
- Related refactoring in one area
- Documentation for one topic

❌ **BAD**:
- Multiple unrelated bug fixes
- Feature + unrelated refactoring
- Mixing types (feat + fix + docs)
- "Various changes" or "WIP"

### Commit Size Guidelines
- **Ideal**: 50-300 lines changed
- **Maximum**: 500 lines (beyond this, split into multiple commits)
- **Exception**: Generated files, dependency updates, large refactors (document why)

### Breaking Changes
Must include `BREAKING CHANGE:` in footer:
```
feat(api)!: redesign authentication flow

BREAKING CHANGE: API endpoints now require OAuth2 instead of API keys.
Clients must update authentication mechanism.
```

## Professional Commit Messages

### Subject Line (First Line)
- **Length**: 50 characters maximum (hard limit: 72)
- **Style**: Imperative mood ("add" not "added" or "adds")
- **Capitalization**: Lowercase after type (except proper nouns)
- **No period**: Don't end with `.`

✅ **GOOD**:
- `feat: add user profile endpoint`
- `fix: resolve memory leak in auth service`
- `refactor: extract duplicate validation logic`

❌ **BAD**:
- `Added new feature for users.` (wrong tense, period, vague)
- `Fix bug` (too vague)
- `WIP` (not descriptive)
- `various updates` (not atomic)

### Body (OPTIONAL but RECOMMENDED)
- **When**: Explain WHY and WHAT, not HOW (code shows how)
- **Format**: Wrap at 72 characters
- **Content**:
  - Motivation for change
  - Contrast with previous behavior
  - Side effects or consequences
  - Reference to issues/tickets

Example:
```
fix(auth): prevent token expiration race condition

Users were experiencing intermittent logouts due to token refresh
racing with expiration checks. This adds a 30-second buffer window
before expiration to ensure refresh completes.

Fixes #123
```

### Footer (OPTIONAL)
- `Fixes #issue`: Closes issue
- `Refs #issue`: References issue
- `BREAKING CHANGE:`: Describes breaking change
- `Reviewed-by:`: Code reviewer (if applicable)

## Gitmoji Usage (OPTIONAL)

### Allowed Gitmojis
Enhance commit types with emojis (use sparingly):

**Features & Fixes**:
- ✨ `:sparkles:` - New feature
- 🐛 `:bug:` - Bug fix
- 🚑 `:ambulance:` - Critical hotfix
- ⚡ `:zap:` - Performance improvement

**Code Quality**:
- ♻️ `:recycle:` - Refactor code
- 🎨 `:art:` - Improve structure/format
- 🔥 `:fire:` - Remove code/files
- ✅ `:white_check_mark:` - Add/update tests

**Documentation**:
- 📝 `:memo:` - Documentation
- 💡 `:bulb:` - Add/update comments

**Dependencies & Config**:
- ⬆️ `:arrow_up:` - Upgrade dependencies
- ⬇️ `:arrow_down:` - Downgrade dependencies
- 🔧 `:wrench:` - Configuration files
- 📦 `:package:` - Update package/deps

**Infrastructure**:
- 🚀 `:rocket:` - Deploy/release
- 👷 `:construction_worker:` - CI/CD
- 🔒 `:lock:` - Security fix
- 🐳 `:whale:` - Docker-related

### Format with Gitmoji
```
<emoji> <type>[scope]: <description>
```

Examples:
- `✨ feat(api): add user pagination endpoint`
- `🐛 fix(auth): resolve token expiration race`
- `♻️ refactor(core): extract agent parsing logic`
- `📝 docs(readme): update installation instructions`

## Pre-Commit Checklist

Before EVERY commit, verify:
- [ ] **NO AI ATTRIBUTION** in commit message or metadata
- [ ] Changes are atomic (one logical change)
- [ ] Commit message follows conventional format
- [ ] Subject line ≤50 chars, imperative mood
- [ ] Code compiles/runs without errors
- [ ] Tests pass (if applicable)
- [ ] No debug code, console.logs, or TODOs
- [ ] Git diff reviewed for unintended changes
- [ ] Staged files are relevant to commit message

## Git Workflow Integration

### Branch Naming
- `feat/description` - Feature branches
- `fix/description` - Bug fix branches
- `refactor/description` - Refactoring branches
- `docs/description` - Documentation branches

### Commit Frequency
- Commit after each atomic change
- Commit when tests pass
- Commit before switching contexts
- DON'T commit broken code

### Before Push
- [ ] All commits follow these rules
- [ ] Rebase if needed to clean history
- [ ] All tests pass
- [ ] No sensitive data in commits

## Examples

### ✅ EXCELLENT Commits

```
feat(api): add pagination to user list endpoint

Implements cursor-based pagination for /api/users endpoint to
improve performance with large datasets. Supports `limit` and
`cursor` query parameters.

Closes #456
```

```
🐛 fix(auth): prevent race condition in token refresh

Token refresh was racing with expiration checks, causing intermittent
logouts. Added 30-second buffer window and mutex lock to ensure
refresh completes before expiration validation.

Fixes #789
```

```
♻️ refactor(core): extract agent parsing into separate module

Moved agent file parsing logic from agents.py to dedicated parser
module to improve testability and separation of concerns. No
functional changes.
```

### ❌ BAD Commits (NEVER DO THIS)

```
various updates

Co-Authored-By: Claude <noreply@anthropic.com>
```
**Problems**: Vague, not atomic, AI attribution

```
Fixed stuff and added features
```
**Problems**: Not conventional, mixing types, vague

```
WIP
```
**Problems**: Not descriptive, not atomic

```
feat: implement the entire authentication system with user management, session handling, password reset, email verification, and OAuth integration
```
**Problems**: Not atomic, too large, should be multiple commits

## Enforcement Priority

**🔴 CRITICAL** (Must follow, no exceptions):
- No AI attribution
- Conventional commit format
- Atomic commits

**🟡 IMPORTANT** (Strong preference):
- Professional commit messages
- Subject line length
- Imperative mood

**🟢 RECOMMENDED** (Best practice):
- Gitmoji usage
- Detailed body text
- Footer references
