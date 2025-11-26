# Basic Memory MCP Server

**Purpose**: Persistent knowledge management through conversations - read/write to a local Markdown knowledge base

## Triggers
- Knowledge persistence needs: "remember this", "save for later", "note this down"
- Cross-session context: "what did we discuss about X", "recall our project"
- Building knowledge graphs: connecting topics, observations, relations
- Personal wiki/notes management during conversations
- Avoiding re-explaining projects to AI sessions

## Tools Available

**Content Management**:
- `write_note()` - Create/update notes with title and content
- `read_note()` - Retrieve notes by title or permalink
- `edit_note()` - Make incremental changes to existing notes
- `delete_note()` - Remove notes from knowledge base

**Knowledge Navigation**:
- `build_context()` - Traverse knowledge graph via memory:// URLs
- `search()` - Query across your knowledge base
- `recent_activity()` - Find recently updated information

## File Format

Notes stored as Markdown with special markup:

**Observations** (facts about topics):
```markdown
- [category] content #tag (optional context)
```

**Relations** (connections between topics):
```markdown
- relation_type [[WikiLink]] (optional context)
```

## Choose When
- **Over manual notes**: When you want AI to help build/maintain knowledge
- **For project context**: Persist project details across sessions
- **For knowledge graphs**: Connect related topics with relations
- **For local storage**: Keep sensitive info on your machine, not cloud

## Works Best With
- **Context7**: Basic Memory stores custom knowledge + Context7 provides library docs
- **Sequential**: Build context from memory → Sequential analyzes complex problems

## Configuration

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "uvx",
      "args": ["basic-memory", "mcp"]
    }
  }
}
```

## Examples
```
"remember our API design decisions" → write_note with structured content
"what did we decide about auth?" → search or read_note
"connect this to our architecture doc" → relations with [[WikiLinks]]
"show recent project notes" → recent_activity
```

## Installation
```bash
uv tool install basic-memory
```

## Resources
- GitHub: https://github.com/basicmachines-co/basic-memory
- License: AGPL-3.0
