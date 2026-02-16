# Architecture Reference Documentation

Visual and textual documentation of the cortex three-layer automation system.

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

### 2. quick-reference.md
**Type**: Cheat Sheet
**Size**: 9.4K
**Format**: Markdown Tables

One-page reference for daily development use.

**Contents**:
- Common commands quick lookup
- Behavioral modes comparison
- Workflows comparison
- Decision guide
- Integration patterns
- Keyboard shortcuts (TUI)
- Typical workflows
- Tips & best practices

**Best for**:
- Daily reference during development
- Quick command lookup
- Pattern examples
- Onboarding cheat sheet

**View**:
```bash
cat docs/reference/architecture/quick-reference.md
```

---

### 3. architecture-diagrams.md
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

### 4. DIAGRAMS_README.md
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

# 2. Try a simple command
cortex
# Press 3 → View Modes
# Press 6 → View Workflows
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

## 📖 The Three-Layer System

```
Layer 1: USER COMMANDS (43 commands, 16 namespaces)
         → What to do
         Examples: /refactor:analyze, /workflow:run

Layer 2: BEHAVIORAL MODES (8 modes)
         → How to operate
         Examples: Brainstorm, Deep_Analysis, Quality_Focus

Layer 3: WORKFLOWS (9 multi-step processes)
         → Step-by-step execution
         Examples: feature-development, refactoring, api-design

Layer 4: EXECUTION (Agents + MCP + Tools)
         → Coordinates specialized agents and tools
         Examples: code-reviewer, Codanna MCP, Sequential
```

---

## 🔗 Integration Example

```
User: /refactor:analyze src/auth
  ↓
Command Layer: Parse and load configuration
  ↓
Mode Layer: Activate Deep_Analysis + Quality_Focus
  ↓
Workflow Layer: Execute refactoring workflow steps 1-3
  ↓
Execution Layer: code-reviewer agent + Codanna MCP
  ↓
Output: Refactoring plan with priorities and risk assessment
```

---

## 📊 System Statistics

- **43** Slash Commands across 16 namespaces
- **8** Behavioral Modes
- **9** Multi-step Workflows
- **25+** Specialized Agents
- **3** MCP Servers (Codanna, Context7, Sequential)

**Coverage Areas**:
- Feature development & bug fixing
- Code refactoring & quality improvement
- API design & implementation
- Security auditing & performance optimization
- Technical debt management
- Developer onboarding
- Architecture review

---

## 🛠️ Installation & Setup

These documentation files are automatically installed with cortex.

**Installation** copies them to:
```
~/.claude/docs/architecture-diagrams.md
~/.claude/docs/quick-reference.md
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

**New Modes**:
- [ ] Update mode count in VISUAL_SUMMARY.txt
- [ ] Add to quick-reference.md modes table
- [ ] Update compatibility matrix in architecture-diagrams.md

**New Workflows**:
- [ ] Update workflow count in VISUAL_SUMMARY.txt
- [ ] Add to quick-reference.md workflows table
- [ ] Add to compatibility matrix

**See DIAGRAMS_README.md** for full update checklist.

---

## 📚 Related Documentation

- `../../guides/` - Step-by-step guides and tutorials
- `../../README.md` - Main documentation index
- `../../../README.md` - Project README
- `~/.claude/commands/` - Slash command definitions
- `~/.claude/modes/` - Behavioral mode definitions
- `~/.claude/workflows/` - Workflow definitions

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

*Last Updated: 2025-11-11*
*Version: 1.0*
*Part of cortex: https://github.com/anthropics/cortex*
