---
name: token-efficiency
description: Compressed communication using symbols and abbreviations. Use when context is limited or brevity is needed.
keywords:
  - compressed communication
  - abbreviations
  - token
  - efficiency
  - token efficiency
---

# Token Efficiency

Compressed communication for limited context windows.

## Symbol System

### Logic & Flow
| Symbol | Meaning |
|--------|---------|
| → | leads to, implies |
| ⇒ | transforms to |
| ← | rollback |
| & | and |
| \| | or |
| » | sequence/then |
| ∴ | therefore |
| ∵ | because |

### Status
| Symbol | Meaning |
|--------|---------|
| ✅ | complete/pass |
| ❌ | failed/error |
| ⚠️ | warning |
| 🔄 | in progress |
| ⏳ | pending |

### Domains
| Symbol | Domain |
|--------|--------|
| ⚡ | performance |
| 🔍 | analysis |
| 🛡️ | security |
| 🏗️ | architecture |

## Abbreviations
- `cfg` config
- `impl` implementation
- `deps` dependencies
- `val` validation
- `perf` performance
- `sec` security
- `err` error

## Examples

**Standard:**
> "The authentication system has a security vulnerability in the user validation function"

**Compressed:**
> `auth.js:45 → 🛡️ sec risk in user val()`

**Standard:**
> "Build completed, now running tests, then deploying"

**Compressed:**
> `build ✅ » test 🔄 » deploy ⏳`

## When to Use
- Context >75% full
- Large codebase analysis
- Complex multi-step workflows
- User requests brevity
