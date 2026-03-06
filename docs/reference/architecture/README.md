# Architecture Reference Documentation

Visual and textual documentation of the cortex architecture.

---

## 📚 Documentation Files

### 1. VISUAL_SUMMARY.txt
**Type**: ASCII Art Diagram
**Size**: 7.2K
**Format**: Plain Text

Quick visual overview perfect for terminal display.

**Contents**:
- System architecture (4 layers)
- Component counts and organization
- Example refactoring flow
- Quick lookup tables
- System statistics

**Best for**:
- Terminal viewing
- Quick reference
- README files
- Presentations

**View**:
```bash
cat docs/reference/architecture/VISUAL_SUMMARY.txt
```

---

### 2. architecture-diagrams.md
**Type**: Comprehensive Diagrams
**Size**: 15K
**Format**: Markdown + Mermaid

Deep dive with 10+ interactive diagrams.

**Contents**:
- System architecture overview (graph)
- Command → Mode → Workflow flow (sequence diagram)
- Mode activation flow (flowchart)
- Workflow execution flow (detailed flowchart)
- Refactoring example: End-to-end (full flow)
- Decision tree: Which layer to use?
- System statistics (pie chart)
- Mode + Workflow compatibility matrix
- Legend and symbols guide
- Quick start guide

**Best for**:
- Learning the system
- Teaching and onboarding
- Architecture reviews
- Understanding integration patterns

**View**:
```bash
# In VS Code with Mermaid extension
code docs/reference/architecture/architecture-diagrams.md

# Online at https://mermaid.live/
# Copy/paste diagrams to view and export
```

---

### 3. DIAGRAMS_README.md
**Type**: Documentation Guide
**Size**: 8.1K
**Format**: Markdown

How to use, read, and maintain all diagrams.

**Contents**:
- Diagram index and descriptions
- How to use each diagram type
- Reading guide (symbols, colors, formats)
- Diagram templates for creating new ones
- Update checklist
- Learning paths (Beginner → Advanced)
- Tools and viewing methods

**Best for**:
- Finding the right diagram
- Understanding diagram conventions
- Creating custom diagrams
- Maintaining documentation

**View**:
```bash
cat docs/reference/architecture/DIAGRAMS_README.md
```

---

## 🎯 Quick Start

### For New Users

**Day 1**: Start here
```bash
# 1. View ASCII summary for quick overview
cat docs/reference/architecture/VISUAL_SUMMARY.txt

# 2. Launch the TUI
cortex tui
```

**Week 1**: Dive deeper
```bash
# 3. Read the cheat sheet
cat docs/reference/architecture/quick-reference.md

# 4. Study the diagrams
# Open architecture-diagrams.md in VS Code or browser
```

### For Developers

**Daily Use**:
- Keep `quick-reference.md` open for command lookup
- Reference `VISUAL_SUMMARY.txt` for system overview
- Use TUI keyboard shortcuts (in quick-reference.md)

**When Learning**:
- Study sequence diagrams in `architecture-diagrams.md`
- Follow the refactoring example end-to-end
- Review decision tree for guidance

### For Architects

**Architecture Reviews**:
- Present system architecture diagram
- Show component distribution
- Explain integration patterns
- Discuss compatibility matrix

**Documentation**:
- Use diagrams in documentation
- Reference decision trees
- Show workflow examples

---

## 📖 System Architecture

```
Agents     → Specialized AI agents with focused responsibilities (29+)
Skills     → Progressive disclosure knowledge packs (127+)
Rules      → Behavioral constraints and best practices
Hooks      → Automation scripts triggered by Claude Code events
Commands   → Slash command definitions for common workflows
```

---

## 📊 System Statistics

- **29+** Specialized Agents
- **127+** Skills
- **3** MCP Servers (Codanna, Context7, Memory)
- Slash commands, rules, and hooks

---

## 🛠️ Installation & Setup

These documentation files are automatically installed with cortex.

**Installation** copies them to:
```
~/.claude/docs/architecture-diagrams.md
~/.claude/docs/DIAGRAMS_README.md
~/.claude/docs/VISUAL_SUMMARY.txt
```

**To reinstall/update documentation**:
```bash
# From project directory
just install

# Or manually copy
cp docs/reference/architecture/* ~/.claude/docs/
```

---

## 🎨 Viewing Diagrams

### ASCII Art (Terminal)
```bash
cat docs/reference/architecture/VISUAL_SUMMARY.txt
# Or from installed location
cat ~/.claude/docs/VISUAL_SUMMARY.txt
```

### Markdown (Any Editor)
```bash
# VS Code, Sublime, etc.
code docs/reference/architecture/quick-reference.md
```

### Mermaid Diagrams

**In VS Code**:
1. Install "Markdown Preview Mermaid Support" extension
2. Open `architecture-diagrams.md`
3. Press `Cmd+Shift+V` (Mac) or `Ctrl+Shift+V` (Windows)

**Online**:
1. Visit https://mermaid.live/
2. Copy diagram from `architecture-diagrams.md`
3. Paste to view and export as PNG/SVG

**Command Line**:
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate images
mmdc -i architecture-diagrams.md -o diagrams.png
```

---

## 🔄 Keeping Documentation Updated

When adding new components:

**New Commands**:
- [ ] Update command count in VISUAL_SUMMARY.txt
- [ ] Add to quick-reference.md command table
- [ ] Update namespace list if new namespace

**See DIAGRAMS_README.md** for full update checklist.

---

## 📚 Related Documentation

- `../../guides/` - Step-by-step guides and tutorials
- `../../README.md` - Main documentation index
- `../../../README.md` - Project README
- `~/.claude/commands/` - Slash command definitions

---

## 🤝 Contributing

To improve these diagrams:

1. **Edit source files** in `docs/reference/architecture/`
2. **Test rendering** with Mermaid preview
3. **Update statistics** if component counts changed
4. **Commit changes** with descriptive message
5. **Reinstall** to update `~/.claude/docs/`

---

## 📞 Getting Help

**Can't find something?**
1. Check VISUAL_SUMMARY.txt for quick overview
2. Search quick-reference.md for specific commands/modes
3. Study architecture-diagrams.md for detailed flows
4. Read DIAGRAMS_README.md for guidance

**Need more diagrams?**
- Review DIAGRAMS_README.md for templates
- Follow color coding and symbol conventions
- Add to appropriate file
- Update this README

---

*Last Updated: 2026-03-06*
*Part of cortex: https://github.com/NickCrew/claude-cortex*
