# Tutorial Design Patterns Reference

Progressive disclosure patterns, exercise types, checkpoint design, difficulty calibration,
prerequisite mapping, and troubleshooting section design.

---

## Progressive Disclosure Patterns

### Pattern 1: Minimal Viable → Full Feature

Start with the smallest working version, then layer features:

```
Step 1: Hello World (just prove it runs)
Step 2: Accept input (add one parameter)
Step 3: Validate input (add error handling)
Step 4: Persist results (add storage)
Step 5: Add UI (add presentation layer)
```

Each step produces a working result. Readers can stop at any step and have something useful.

### Pattern 2: Concrete → Abstract

Show the specific case first, then generalize:

```
Step 1: Hard-code a specific example
Step 2: Replace hard-coded values with variables
Step 3: Extract into a reusable function
Step 4: Discuss when to use the pattern
```

### Pattern 3: Happy Path → Edge Cases

Get the basic case working before handling complexity:

```
Step 1: Handle the normal case
Step 2: What if input is empty?
Step 3: What if the network fails?
Step 4: What about concurrent access?
```

### Pattern 4: Visual → Code → Theory

For concept-heavy topics:

```
Step 1: Diagram showing what happens
Step 2: Code that implements it
Step 3: Explanation of why it works
Step 4: When to use (and not use) this approach
```

---

## Exercise Types

### Fill-in-the-Blank

**Purpose**: Reinforce syntax and patterns just introduced.

**Template**:
```markdown
### Exercise: Complete the middleware

Fill in the blanks to create an authentication middleware:

\`\`\`javascript
function authMiddleware(req, res, next) {
  const token = req.headers[______];  // 1. Which header?

  if (!token) {
    return res.status(______).json({   // 2. Which status code?
      error: "Authentication required"
    });
  }

  try {
    const decoded = jwt.verify(token, ______);  // 3. What to verify against?
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(______).json({   // 4. Which status code for invalid token?
      error: "Invalid token"
    });
  }
}
\`\`\`

<details>
<summary>Solution</summary>

1. `'authorization'`
2. `401`
3. `process.env.JWT_SECRET`
4. `403`

</details>
```

### Debug Challenge

**Purpose**: Teach error reading and common mistakes.

**Template**:
```markdown
### Exercise: Fix the bug

This code should fetch user data, but it fails silently. Find and fix the issue:

\`\`\`javascript
// BUG: This function never returns the user data
async function getUser(id) {
  const response = fetch(`/api/users/${id}`);
  const data = response.json();
  return data;
}
\`\`\`

**Hints**:
1. Check what `fetch` returns...
2. What keyword is missing?

<details>
<summary>Solution</summary>

Missing `await` on both async operations:
\`\`\`javascript
async function getUser(id) {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  return data;
}
\`\`\`

</details>
```

### Extension Task

**Purpose**: Build confidence by adding to working code.

**Template**:
```markdown
### Exercise: Add pagination

The API currently returns all results. Add pagination support:

**Requirements**:
- Accept `page` and `limit` query parameters
- Default to page 1, limit 20
- Return total count in the response
- Return next/previous page links

**Starting code**: Use the server from the previous section.

**Hints**:
1. `req.query.page` gives you the query parameter
2. SQL: `LIMIT ? OFFSET ?`
3. Offset = (page - 1) * limit
```

### From Scratch

**Purpose**: Verify the reader can apply concepts independently.

**Template**:
```markdown
### Exercise: Build a rate limiter

Using what you've learned about middleware and Redis, build a rate limiter that:

- Limits each IP to 100 requests per minute
- Returns 429 Too Many Requests when exceeded
- Includes a `Retry-After` header

**No starter code provided.** Refer back to the middleware and Redis sections if needed.
```

### Refactoring

**Purpose**: Teach code improvement and design thinking.

**Template**:
```markdown
### Exercise: Refactor for testability

This function works but is hard to test because it directly calls the database:

\`\`\`javascript
async function createUser(name, email) {
  const db = require('./database');
  const existing = await db.query('SELECT id FROM users WHERE email = ?', [email]);
  if (existing.length > 0) throw new Error('Email taken');
  return db.query('INSERT INTO users (name, email) VALUES (?, ?)', [name, email]);
}
\`\`\`

Refactor it so the database dependency can be injected for testing.
```

---

## Checkpoint Design

### When to Insert Checkpoints

- After every major concept introduction
- After every exercise
- Before moving to a new topic area
- At natural "save points" where progress is visible

### Checkpoint Template

```markdown
### Checkpoint

At this point you should have:
- [ ] [Concrete, verifiable state 1]
- [ ] [Concrete, verifiable state 2]
- [ ] [Concrete, verifiable state 3]

**Verify it works**:
\`\`\`bash
[command to run that shows success]
\`\`\`

**Expected output**:
\`\`\`
[exact output the reader should see]
\`\`\`

> **Something wrong?** Check the [Troubleshooting](#troubleshooting) section,
> or compare your code against the [checkpoint snapshot](link).
```

### Checkpoint Principles

- **Observable**: The reader should see concrete evidence of progress
- **Reversible**: If the checkpoint fails, the reader knows where to look
- **Quick**: Verification should take seconds, not minutes
- **Binary**: Either it works or it doesn't — no ambiguity

---

## Difficulty Calibration

### Difficulty Levels

| Level | Reader Profile | Content Style |
|-------|---------------|---------------|
| **Beginner** | No prior experience with this specific technology | Every step explicit, nothing assumed |
| **Intermediate** | Comfortable with basics, wants to go deeper | Some steps condensed, focus on "why" |
| **Advanced** | Experienced, learning specific patterns | Concise, focus on trade-offs and edge cases |

### Calibration Rules

1. **State the level** — tell readers upfront who this is for
2. **One level per tutorial** — do not mix beginner and advanced in one doc
3. **Prerequisites bridge levels** — "This tutorial assumes you completed the Getting Started guide"
4. **Explicit vs implicit steps**:
   - Beginner: "Open your terminal. Type `npm init -y` and press Enter."
   - Intermediate: "Initialize a new Node project with `npm init -y`."
   - Advanced: "Scaffold the project (we'll assume standard Node tooling)."

### Pacing Guide

| Level | New concepts per section | Code-to-text ratio | Exercise frequency |
|-------|------------------------|--------------------|--------------------|
| Beginner | 1 | 60% code, 40% explanation | Every section |
| Intermediate | 1-2 | 50% code, 50% explanation | Every 2-3 sections |
| Advanced | 2-3 | 70% code, 30% explanation | End of chapter |

---

## Prerequisite Mapping

### Prerequisite Types

| Type | Description | How to specify |
|------|-------------|---------------|
| **Knowledge** | Concepts the reader must already understand | "Familiarity with JavaScript promises" |
| **Setup** | Tools and environment that must be installed | "Node.js 18+ and npm installed" |
| **Completion** | Prior tutorials or guides that must be finished | "Complete the Getting Started tutorial" |
| **Access** | Accounts or resources needed | "An AWS account with admin access" |

### Prerequisite Documentation Template

```markdown
## Prerequisites

### Required Knowledge
- [ ] JavaScript ES6+ (arrow functions, destructuring, async/await)
- [ ] Basic HTTP concepts (methods, status codes, headers)

### Required Setup
- [ ] Node.js 18 or later ([install guide](link))
- [ ] A code editor (VS Code recommended)
- [ ] A terminal (any shell)

### Required Accounts
- [ ] GitHub account ([sign up](link))

### Prior Tutorials
- [ ] [Getting Started with Express](link) — we build on the server from this tutorial
```

### Prerequisite Verification

Where possible, give commands to verify prerequisites:

```markdown
Verify your setup before starting:

\`\`\`bash
node --version    # Should output v18.x or higher
npm --version     # Should output 9.x or higher
git --version     # Should output 2.x or higher
\`\`\`
```

---

## Troubleshooting Section Design

### Structure

Place troubleshooting at the end of each major section and a consolidated version
at the end of the tutorial.

### Entry Format

```markdown
**Error: `ECONNREFUSED: connect ECONNREFUSED 127.0.0.1:5432`**

The database server is not running.

**Fix**:
\`\`\`bash
# macOS (Homebrew)
brew services start postgresql

# Linux (systemd)
sudo systemctl start postgresql

# Docker
docker start my-postgres-container
\`\`\`

**Still not working?** Check that PostgreSQL is configured to accept local connections
in `pg_hba.conf`.
```

### Common Error Categories

| Category | Examples | Typical cause |
|----------|---------|---------------|
| **Environment** | Missing binary, wrong version | Setup not complete |
| **Network** | Connection refused, timeout | Service not running or port conflict |
| **Permission** | EACCES, permission denied | Wrong user or file permissions |
| **Syntax** | Unexpected token, parse error | Typo in code |
| **State** | Not found, already exists | Steps done out of order |
| **Dependency** | Module not found, version conflict | Missing or incompatible package |

### Troubleshooting Principles

1. **Show the exact error message** — readers search by error text
2. **Explain why it happens** — not just how to fix it
3. **Provide the fix command** — copy-paste ready
4. **Include a fallback** — "If that doesn't work, try..."
5. **Link to deeper resources** — for complex issues beyond tutorial scope
