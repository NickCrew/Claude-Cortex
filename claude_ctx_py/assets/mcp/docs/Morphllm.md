# Morphllm MCP Server

**Purpose**: Bulk code transformations, pattern-based edits, and style enforcement across files

## Triggers
- Mass refactoring across multiple files
- Pattern-based code transformations
- Code style enforcement and standardization
- API migration (v1 → v2 patterns)
- Bulk renaming with semantic awareness
- Codemod-style operations at scale

## Choose When
- **Over manual edits**: When changing >5 files with same pattern
- **Over find-replace**: When transformations are semantic, not textual
- **For consistency**: Enforcing patterns across codebase
- **For migrations**: Updating to new APIs or frameworks
- **For refactoring**: Systematic renames, moves, or restructuring
- **For style fixes**: Applying linting rules en masse

## Works Best With
- **Codanna**: Codanna finds symbols → Morphllm transforms all occurrences
- **Sequential**: Sequential designs migration → Morphllm applies changes
- **Code Review**: Morphllm transforms → Review validates changes

## Core Capabilities
- **Pattern matching**: Find code patterns semantically
- **AST-aware transformations**: Understand code structure, not just text
- **Bulk operations**: Apply changes across entire codebase
- **Type-safe refactoring**: Maintain type correctness during transforms
- **Rollback support**: Undo transformations if needed
- **Dry-run mode**: Preview changes before applying

## Transformation Types

### Rename Operations
- Variables, functions, classes
- Imports and exports
- Type definitions
- File and directory names

### Pattern Transformations
- Function signature changes
- API call updates (old → new)
- Hook conversions (class → functional)
- Promise → async/await
- Callbacks → Promises

### Style Enforcement
- Import organization
- Code formatting alignment
- Naming convention fixes
- Remove unused code
- Add missing types

## Examples
```
"rename UserService to AuthService everywhere" → Morphllm (semantic rename)
"convert all class components to hooks" → Morphllm (pattern transformation)
"update all API calls to v2 format" → Morphllm (migration pattern)
"fix all import ordering" → Morphllm (style enforcement)
"remove all console.log statements" → Morphllm (bulk cleanup)
"rename this one variable" → Native edit (single-file operation)
```

## Safety Features

### Pre-Transformation Checks
- [ ] Parse all target files successfully
- [ ] Validate transformation rules
- [ ] Check for potential conflicts
- [ ] Verify type safety maintained

### During Transformation
- [ ] Apply changes atomically per file
- [ ] Maintain syntax validity
- [ ] Preserve code semantics
- [ ] Track all modifications

### Post-Transformation
- [ ] Run automated tests
- [ ] Verify build succeeds
- [ ] Check type checking passes
- [ ] Generate change report

## Performance Considerations
- **File scanning**: Parallel processing for large codebases
- **Incremental mode**: Only process changed files
- **Caching**: Store parsed ASTs for reuse
- **Batch size**: Control memory usage with file batching

## Integration Patterns

### With Codanna (Codebase-Wide Refactor):
```
1. Codanna: Find all usages of old pattern
2. Morphllm: Transform to new pattern
3. Codanna: Verify transformation completeness
```

### With Sequential (Migration Planning):
```
1. Sequential: Design migration strategy
2. Morphllm: Apply transformations
3. Sequential: Validate migration success
```

### With Code Review (Quality Assurance):
```
1. Morphllm: Apply bulk transformations
2. Code Review: Validate changes
3. Morphllm: Adjust based on feedback
```

## Dry-Run Workflow

Always test transformations first:

```bash
# Step 1: Preview changes
morphllm --dry-run transform-pattern.ts

# Step 2: Review diff
git diff

# Step 3: Apply if satisfied
morphllm transform-pattern.ts

# Step 4: Validate
npm test
```

## Common Patterns

### API Migration
```typescript
// Before: v1 API
apiClient.get('/users')

// After: v2 API
apiClient.users.list()
```

### Hook Conversion
```typescript
// Before: Class component
class UserProfile extends Component { ... }

// After: Functional component
function UserProfile() { ... }
```

### Import Cleanup
```typescript
// Before: Messy imports
import { z } from 'zod'
import React from 'react'
import { useState } from 'react'

// After: Organized
import React, { useState } from 'react'
import { z } from 'zod'
```

## Quality Gates
When using Morphllm, ensure:
- [ ] Dry-run reviewed before applying
- [ ] All tests pass after transformation
- [ ] Type checking succeeds
- [ ] Build completes successfully
- [ ] No unintended changes introduced
- [ ] Transformation rules documented
- [ ] Rollback plan ready if needed
