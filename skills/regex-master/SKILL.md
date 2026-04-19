---
name: regex-master
description: 'Use this skill when building, explaining, or debugging regular expressions for pattern matching, validation, or text extraction. Trigger phrases: ''write a regex'', ''match this pattern'', ''validate this format'', ''extract from text''. Not for natural language parsing or full grammar parsing (use a parser instead).'
version: 1.0.0
author: community
tags:
  - coding
  - regex
  - pattern-matching
  - text-processing
license: MIT
keywords:
  - regex
  - pattern matching
  - text extraction
  - master
  - regex master
---

# Regex Master

## Overview
The Regex Master skill covers building correct, readable, and efficient regular expressions for common text processing tasks. It explains character classes, quantifiers, groups, alternation, anchors, and lookahead/lookbehind assertions. It includes a quick-reference library of battle-tested patterns for emails, URLs, dates, phone numbers, IP addresses, and log lines. Every regex is explained token by token so you understand what it does rather than just copying it.

## When to Use
- Validating user input (email, phone, postal code, URL)
- Extracting structured data from unstructured text (logs, documents, HTML attributes)
- Search-and-replace with patterns in code editors or scripts
- Parsing delimited or fixed-format text files
- Filtering or transforming data with `grep`, `sed`, `awk`, Python, or JavaScript

## When NOT to Use
- Parsing HTML or XML (use a DOM parser: BeautifulSoup, DOMParser — regex is unreliable for nested structures)
- Parsing programming languages or complex grammars (use a proper parser/AST)
- Matching natural language semantics (use NLP tools)
- When a simple string split or indexOf is sufficient — don't reach for regex when a simpler tool works

## Quick Reference

### Building Blocks
| Token | Meaning | Example | Matches |
|-------|---------|---------|---------|
| `.` | Any character except newline | `a.c` | `abc`, `a1c`, `a-c` |
| `\d` | Digit `[0-9]` | `\d+` | `42`, `007` |
| `\w` | Word char `[a-zA-Z0-9_]` | `\w+` | `hello`, `foo_2` |
| `\s` | Whitespace | `\s+` | space, tab, newline |
| `\D` | Non-digit | `\D` | `a`, `-`, ` ` |
| `\W` | Non-word char | `\W` | `!`, `@`, ` ` |
| `\S` | Non-whitespace | `\S+` | `hello`, `42` |
| `^` | Start of string/line | `^Hello` | `Hello world` |
| `$` | End of string/line | `world$` | `Hello world` |
| `\b` | Word boundary | `\bcat\b` | `the cat sat` (not `catch`) |
| `[abc]` | Character class | `[aeiou]` | any vowel |
| `[^abc]` | Negated class | `[^0-9]` | any non-digit |
| `[a-z]` | Range | `[a-zA-Z]` | any letter |

### Quantifiers
| Quantifier | Meaning | Greedy? |
|-----------|---------|---------|
| `*` | 0 or more | Yes |
| `+` | 1 or more | Yes |
| `?` | 0 or 1 (optional) | Yes |
| `{n}` | Exactly n | Yes |
| `{n,m}` | Between n and m | Yes |
| `{n,}` | n or more | Yes |
| `*?` | 0 or more | No (lazy) |
| `+?` | 1 or more | No (lazy) |

### Groups & References
| Syntax | Meaning |
|--------|---------|
| `(abc)` | Capturing group |
| `(?:abc)` | Non-capturing group |
| `(?P<name>abc)` | Named capturing group (Python) |
| `(?<name>abc)` | Named capturing group (JS/PCRE) |
| `\1`, `$1` | Back-reference to group 1 |
| `a\|b` | Alternation: a or b |

### Lookaround
| Syntax | Meaning |
|--------|---------|
| `(?=abc)` | Positive lookahead: followed by abc |
| `(?!abc)` | Negative lookahead: NOT followed by abc |
| `(?<=abc)` | Positive lookbehind: preceded by abc |
| `(?<!abc)` | Negative lookbehind: NOT preceded by abc |

### Flags
| Flag | Effect |
|------|--------|
| `i` / `re.IGNORECASE` | Case-insensitive |
| `m` / `re.MULTILINE` | `^`/`$` match line boundaries |
| `s` / `re.DOTALL` | `.` matches newlines |
| `g` | Global — find all matches (JS) |
| `x` / `re.VERBOSE` | Allow whitespace/comments in pattern |

### Common Patterns Library
| Pattern | Regex |
|---------|-------|
| Email (simple) | `^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$` |
| URL | `https?://[\w.-]+(?:/[\w./?=#&%-]*)?` |
| IPv4 | `\b(?:\d{1,3}\.){3}\d{1,3}\b` |
| Date (YYYY-MM-DD) | `\d{4}-(?:0[1-9]\|1[0-2])-(?:0[1-9]\|[12]\d\|3[01])` |
| Time (HH:MM:SS) | `(?:[01]\d\|2[0-3]):[0-5]\d:[0-5]\d` |
| US Phone | `\+?1?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}` |
| ZIP code (US) | `\d{5}(?:-\d{4})?` |
| Credit card | `\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b` |
| Hex color | `#(?:[0-9a-fA-F]{3}\|[0-9a-fA-F]{6})\b` |
| UUID | `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` |
| Semantic version | `\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?` |
| HTML tag (simple) | `<([a-z][a-z0-9]*)\b[^>]*>(.*?)</\1>` |
| Slug | `^[a-z0-9]+(?:-[a-z0-9]+)*$` |

## Instructions

1. **Define what to match precisely in plain English first**
   - What does a valid match look like? (examples)
   - What should NOT match? (counter-examples)
   - Where in the string must it appear? (anywhere, start, full string)

2. **Build the regex incrementally**
   - Start with the simplest pattern that matches one known good example.
   - Add character classes, quantifiers, and anchors one at a time.
   - Test after each addition against both positive and negative examples.

3. **Anchor appropriately**
   - Use `^...$` for full-string validation (email, phone, slug).
   - Omit anchors for searching within a larger text.
   - Use `\b` for word-boundary matching to avoid partial matches.

4. **Choose capturing vs. non-capturing groups**
   - Use `(?:...)` for grouping without capturing when you don't need the group's value.
   - Use named groups `(?P<year>\d{4})` for readability and reliable extraction.

5. **Handle edge cases explicitly**
   - Optional parts: `(?:\.com)?` — the `?` makes the group optional.
   - Unicode: use `re.UNICODE` flag or `\p{L}` (PCRE2) for non-ASCII letters.
   - Newlines: use the `s` / `DOTALL` flag if `.` should match newlines.

6. **Test thoroughly**
   - Test against: typical valid input, edge-of-valid input, invalid input that looks similar.
   - Use online tools: regex101.com (with detailed explanation), regexr.com.

7. **Document the regex**
   - Always add a comment explaining what the regex matches.
   - Use verbose mode (`re.VERBOSE` in Python) to add inline comments for complex patterns.

## Examples

### Example 1: Validate an email address

**Input:** "Write a regex to validate email addresses."

**Output:**

```python
import re

# Email validation regex
# Allows: local part with letters, digits, dots, plus, hyphen
# Requires: @ symbol
# Domain: letters, digits, hyphens
# TLD: 2+ letters
EMAIL_REGEX = re.compile(
    r'^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$',
    re.IGNORECASE
)

# Verbose version explaining each token:
EMAIL_REGEX_VERBOSE = re.compile(r'''
    ^               # Start of string
    [\w.+-]+        # Local part: word chars, dots, plus, hyphen (1 or more)
    @               # Literal @ symbol
    [\w-]+          # Domain name: word chars and hyphens (1 or more)
    \.              # Literal dot (escaped)
    [a-zA-Z]{2,}   # TLD: 2 or more letters
    $               # End of string
''', re.VERBOSE | re.IGNORECASE)

def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))

# Tests
assert validate_email("alice@example.com") == True
assert validate_email("alice.smith+tag@sub.domain.org") == True
assert validate_email("alice@example.c") == False   # TLD too short
assert validate_email("@example.com") == False      # Missing local part
assert validate_email("alice@.com") == False        # Missing domain
assert validate_email("alice example.com") == False # Missing @
```

**What it matches / rejects:**
```
✅ alice@example.com
✅ alice.smith+filter@sub.domain.co.uk
✅ user123@my-company.io
❌ alice@example.c       (TLD must be 2+ chars)
❌ alice @example.com    (spaces not allowed)
❌ alice@@example.com    (double @)
❌ @example.com          (empty local part)
```

> **Note:** RFC 5321 email validation is extremely complex. This regex covers ~99% of real-world valid addresses. For production, combine with a verification email.

---

### Example 2: Extract data from log lines

**Input:** Parse Apache Combined Log Format lines:
```
192.168.1.1 - frank [10/Oct/2024:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326 "http://example.com/" "Mozilla/5.0"
```

**Output:**

```python
import re
from datetime import datetime

LOG_PATTERN = re.compile(r'''
    ^
    (?P<ip>\d{1,3}(?:\.\d{1,3}){3})  # Client IP address
    \s-\s                              # Separator " - "
    (?P<user>\S+)                      # Remote user (- if none)
    \s
    \[(?P<timestamp>[^\]]+)\]          # Timestamp in brackets
    \s
    "(?P<method>[A-Z]+)                # HTTP method
    \s(?P<path>[^\s"]+)                # Request path
    \s(?P<protocol>HTTP/[\d.]+)"       # Protocol
    \s
    (?P<status>\d{3})                  # HTTP status code
    \s
    (?P<size>\d+|-)                    # Response size (or - if none)
    (?:\s"(?P<referer>[^"]*)")?        # Optional referer
    (?:\s"(?P<user_agent>[^"]*)")?     # Optional user agent
    $
''', re.VERBOSE)

def parse_log_line(line: str) -> dict | None:
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None
    data = match.groupdict()
    data['status'] = int(data['status'])
    data['size'] = int(data['size']) if data['size'] != '-' else 0
    return data

# Test
line = '192.168.1.1 - frank [10/Oct/2024:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326 "http://example.com/" "Mozilla/5.0"'
result = parse_log_line(line)
print(result)
# {
#   'ip': '192.168.1.1', 'user': 'frank',
#   'timestamp': '10/Oct/2024:13:55:36 -0700',
#   'method': 'GET', 'path': '/index.html',
#   'protocol': 'HTTP/1.1', 'status': 200,
#   'size': 2326, 'referer': 'http://example.com/',
#   'user_agent': 'Mozilla/5.0'
# }
```

JavaScript equivalent for the same pattern:
```javascript
const LOG_PATTERN = /^(\d{1,3}(?:\.\d{1,3}){3}) - (\S+) \[([^\]]+)\] "([A-Z]+) ([^\s"]+) (HTTP\/[\d.]+)" (\d{3}) (\d+|-)(?: "([^"]*)")?(?: "([^"]*)")?$/;

function parseLogLine(line) {
  const m = line.match(LOG_PATTERN);
  if (!m) return null;
  const [, ip, user, timestamp, method, path, protocol, status, size, referer, userAgent] = m;
  return { ip, user, timestamp, method, path, protocol, status: +status, size: size === '-' ? 0 : +size, referer, userAgent };
}
```

## Best Practices
- Build complex regex with named groups and verbose mode for readability
- Never use regex for HTML/XML parsing — use a DOM parser
- Test with regex101.com for interactive debugging and explanation
- Prefer specific character classes (`[a-z]`) over `.` + filter to avoid surprise matches
- Use lazy quantifiers (`+?`, `*?`) when you need the shortest match, not the longest
- Compile regex patterns once and reuse (`re.compile()`) in performance-critical code

## Common Mistakes
- Using `.*` (greedy) when you want the shortest match — use `.*?` (lazy)
- Forgetting to escape `.` — unescaped `.` matches any character
- Using `^`/`$` when multiline mode is needed (they match string boundaries by default, not line boundaries)
- Catastrophic backtracking with nested quantifiers like `(a+)+` on long non-matching input
- Not anchoring validation patterns — `\d+` matches the digits in `abc123def`
- Using capturing groups `()` when non-capturing `(?:)` is sufficient — wastes memory

## Tips & Tricks
- regex101.com shows a detailed token-by-token explanation and live testing
- `re.fullmatch()` in Python is safer than `re.match()` for validation — no partial matches
- In JavaScript, prefer named groups: `/(?<year>\d{4})-(?<month>\d{2})/` — access via `match.groups.year`
- Use `sed -E` or `grep -P` for extended/PCRE regex on the command line
- Atomic groups `(?>...)` (PCRE) prevent backtracking — useful for catastrophic backtracking prevention

## Related Skills
- [sql-expert](../sql-expert/SKILL.md)
- [security-auditor](../security-auditor/SKILL.md)
- [test-writer](../test-writer/SKILL.md)
