# Codanna Code Intelligence

**Use codanna MCP tools before grep/find for code discovery and analysis.**

## Quick Reference

- `semantic_search_docs query:"..."` — Find code by intent/concept
- `find_symbol name:"..."` — Get symbol details (function, class, etc.)
- `find_callers symbol:"..."` — Who calls this?
- `get_calls symbol:"..."` — What does this call?
- `analyze_impact symbol:"..."` — What breaks if I change this?

## When to Use

- Searching for where something is implemented → `semantic_search_docs`
- Understanding a function before modifying it → `find_symbol` + `get_calls`
- Refactoring shared code → `analyze_impact` first
- Tracing bugs through call chains → `find_callers`

Codanna understands code structure. Grep finds text. Use the right tool.
