# Codanna MCP Server

**Purpose**: Code intelligence, semantic understanding, and impact analysis for large codebases

## Triggers
- Symbol-based operations: navigation, search, definitions
- Large codebase exploration and understanding
- Impact analysis and dependency mapping
- Semantic code search beyond grep patterns
- Change impact assessment and refactoring safety
- Cross-file navigation and symbol relationships

## Choose When
- **Over native tools**: When you need semantic understanding vs literal matching
- **Over WebSearch**: For internal project knowledge and code relationships
- **For large codebases**: When grep/find aren't sufficient for discovery
- **For refactoring**: When you need to understand change impact radius
- **For symbol navigation**: Jump-to-definition, find-references workflows
- **For architecture understanding**: Map relationships between components

## Works Best With
- **Sequential**: Codanna finds symbols → Sequential analyzes architecture
- **Context7**: Codanna explores project → Context7 provides framework patterns
- **Magic**: Codanna identifies components → Magic generates UI patterns

## Core Capabilities

### Tier 1 (Primary Operations)
- **semantic_search_with_context**: Find relevant code with surrounding context
  - Use for: Understanding how features work, finding implementation patterns
  - Returns: Code snippets with file paths and contextual information

- **analyze_impact**: Map dependencies and change radius
  - Use for: Refactoring safety, understanding what will break
  - Returns: Dependency graph and affected components

### Tier 2 (Symbol Operations)
- **find_symbol**: Locate symbol definitions across the codebase
  - Use for: Jump-to-definition, finding where things are defined
  - Returns: Symbol locations with file and line numbers

- **get_calls**: Find what a function/method calls
  - Use for: Understanding function dependencies
  - Returns: List of called functions/methods

- **find_callers**: Find what calls a function/method
  - Use for: Understanding usage and impact
  - Returns: List of callers with locations

### Tier 3 (Discovery & Metadata)
- **search_symbols**: Search for symbols by name pattern
  - Use for: Discovering available functions/classes
  - Returns: Matching symbol names and locations

- **semantic_search_docs**: Search documentation and comments
  - Use for: Finding explained concepts and documented behavior
  - Returns: Documentation snippets with context

- **get_index_info**: Get indexing status and statistics
  - Use for: Verify indexing complete before operations
  - Returns: Index metadata and coverage info

## Recommended Workflow

1. **Start Broad**: Use `semantic_search_with_context` to understand the area
2. **Assess Impact**: Use `analyze_impact` before making changes
3. **Navigate Precisely**: Use `find_symbol`, `get_calls`, `find_callers` for specifics
4. **Verify Safety**: Check impact analysis before refactoring

## Examples

### Understanding a Feature
```
"How does user authentication work?"
→ Codanna semantic_search_with_context("user authentication")
→ Returns code with context showing auth flow
```

### Safe Refactoring
```
"Rename getUserData function"
→ Codanna analyze_impact("getUserData")
→ Shows all callers and dependencies
→ Safe to refactor with full knowledge of impact
```

### Symbol Navigation
```
"Where is AuthService defined?"
→ Codanna find_symbol("AuthService")
→ Returns exact file and line number
```

### Dependency Analysis
```
"What does processPayment call?"
→ Codanna get_calls("processPayment")
→ Returns all dependencies
```

### Usage Discovery
```
"What calls the validateToken function?"
→ Codanna find_callers("validateToken")
→ Returns all usage sites
```

## Performance Considerations
- **Indexing**: First use may require project indexing
- **Large projects**: Optimized for codebases with 10K+ files
- **Query speed**: Sub-second operations after indexing
- **Cache efficiency**: Frequently accessed symbols cached

## Integration Patterns

### With Sequential (Architecture Analysis)
```
1. Codanna: Map component relationships with analyze_impact
2. Sequential: Reason about architectural improvements
3. Codanna: Verify changes won't break dependencies
```

### With Context7 (Framework Compliance)
```
1. Codanna: Identify existing patterns with semantic_search
2. Context7: Verify against framework documentation
3. Codanna: Find all places needing updates
```

## Quality Gates
When using Codanna, ensure:
- [ ] Index is up-to-date before symbol operations
- [ ] Impact analysis completed before major refactoring
- [ ] Semantic queries specific enough for accuracy
- [ ] Cross-file dependencies validated
- [ ] Change radius understood and acceptable
