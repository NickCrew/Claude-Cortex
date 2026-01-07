# Credits & Attribution

This project builds upon ideas, patterns, and content from several excellent open-source projects in the Claude Code ecosystem.

## Adapted Content & Derived Works

### Superpowers
**Repository:** [obra/superpowers](https://github.com/obra/superpowers)
**License:** MIT License
**Attribution:** Significant portions of cortex's skills, logic patterns, and intelligent activation system were directly copied and adapted from obra/superpowers.

**Skills Adapted (from 54 total skills):**
At least 10+ skills in the `skills/` directory are derived from Superpowers, including:
- `systematic-debugging` - Root cause analysis framework
- `test-driven-development` - TDD workflow patterns
- `verification-before-completion` - Quality gate enforcement
- `requesting-code-review` - Code review request patterns
- `receiving-code-review` - Code review response handling
- `subagent-driven-development` - Multi-agent development workflows
- `using-git-worktrees` - Git worktree management
- `testing-skills-with-subagents` - Skill testing methodology
- `sharing-skills` - Skill contribution workflows
- `writing-skills` - Skill creation patterns
- `collaboration/brainstorming` - Collaborative discovery workflows
- `collaboration/executing-plans` - Plan execution discipline
- Additional workflow and quality-focused skills

**Logic & Concepts Adapted:**
- Intelligent skill activation based on context detection
- Auto-activation triggers and pattern matching
- Skill dependency management and orchestration
- Systematic problem-solving workflows
- Quality-first development enforcement
- Verification-before-completion patterns

**Commands & Modes Influenced:**
Many of our slash commands and behavioral modes are heavily influenced by Superpowers' workflow patterns and execution discipline.

These skills and logic patterns have been adapted and modified to fit the cortex framework while maintaining the original MIT License. See `skills/LICENSE.superpowers` for full license text and proper attribution.

### SuperClaude Framework
**Repository:** [SuperClaude-Org/SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework)
**License:** MIT License
**Attribution:** Multiple agents, behavioral modes concepts, slash command patterns, and MCP integration architecture were directly copied and adapted from SuperClaude Framework.

**Agents Adapted (from 9 total agents):**
Several agents in the `agents/` directory are derived from SuperClaude, including specialized personas for:
- Development workflows (code-reviewer, debugger)
- Infrastructure management (cloud-architect, deployment-engineer, kubernetes-architect, terraform-specialist)
- Language specialists (python-pro, typescript-pro)
- Security (security-auditor)

**Architectural Patterns Adapted:**
- Behavioral modes system for context-aware workflows (`modes/` directory)
- Slash command architecture (`commands/` directory structure)
- MCP (Model Context Protocol) server integration patterns
- Multi-agent orchestration concepts
- Session memory and documentation-driven development patterns

SuperClaude's comprehensive framework for transforming Claude Code into a structured development platform fundamentally shaped our approach to modes, commands, agent orchestration, and MCP integration.

### VoltAgent Awesome Claude Code Subagents
**Repository:** [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
**License:** MIT License
**Attribution:** Multiple specialized agents were directly copied and adapted from VoltAgent's awesome-claude-code-subagents collection.

**Agents Adapted (from 9 total agents):**
Several agents in the `agents/` directory are derived from VoltAgent's 100+ agent collection, including:
- Full-stack development specialists
- DevOps and infrastructure agents
- Language-specific experts
- Quality and security focused agents

**Organizational Patterns Adapted:**
- Hierarchical agent categorization (10 major categories)
- Domain-specific context windows and permissions
- Production-ready agent templates
- Agent metadata and dependency tracking

The concept of organizing 100+ specialized agents into coherent categories directly informed our agent management system, the TUI's agent activation interface, and our agent metadata schema.

### Anthropic Official Skills
**Copyright:** © 2025 Anthropic, PBC. All rights reserved.
**License:** Anthropic Terms of Service
**Attribution:** Several skills in the `skills/document-skills/` directory are official Anthropic skills.

Skills licensed from Anthropic include:
- `document-skills/pdf/` - PDF generation and manipulation
- `document-skills/docx/` - Microsoft Word document handling
- `document-skills/pptx/` - PowerPoint presentation creation
- `document-skills/xlsx/` - Excel spreadsheet operations
- `canvas-design/` - Visual design and canvas creation (Apache 2.0)
- `webapp-testing/` - Web application testing patterns

These skills are used under Anthropic's Terms of Service and are subject to restrictions on extraction, reproduction, and derivative works. See individual `LICENSE.txt` files in each skill directory for specific terms.

## Inspirations & Architectural Patterns

The following projects inspired architectural decisions, design patterns, and workflow concepts in cortex (no direct code copying):

### Code CLI
**Repository:** [just-every/code](https://github.com/just-every/code)
**License:** Apache-2.0 License
**Inspiration:**
- Multi-agent orchestration patterns
- Unified settings architecture for centralized configuration
- Reasoning control mechanisms (depth/effort levels)
- Developer ergonomics and CLI design philosophy
- Theme customization system

Code's emphasis on developer experience, local-first architecture, and reasoning controls informed our TUI design, settings management, and the thinking budget system.

## Technology Stack Credits

### Python Textual TUI Framework
**Project:** [Textualize/textual](https://github.com/Textualize/textual)
**License:** MIT License
The beautiful terminal UI is built with Textual, an amazing framework for building sophisticated terminal applications.

### Rich Terminal Formatting
**Project:** [Textualize/rich](https://github.com/Textualize/rich)
**License:** MIT License
Console output formatting, progress bars, and syntax highlighting powered by Rich.

### PyYAML
**Project:** [yaml/pyyaml](https://github.com/yaml/pyyaml)
**License:** MIT License
YAML parsing for agents, modes, commands, and configuration files.

### Python Click
**Project:** [pallets/click](https://github.com/pallets/click)
**License:** BSD-3-Clause License
Command-line interface framework providing the foundation for `cortex` CLI.

## Documentation & Design

### Jekyll & Minima Theme
**Project:** [jekyll/minima](https://github.com/jekyll/minima)
**License:** MIT License
GitHub Pages documentation site built with Jekyll and the Minima theme.

### Reveal.js Presentations
**Project:** [hakimel/reveal.js](https://github.com/hakimel/reveal.js)
**License:** MIT License
Interactive presentations powered by Reveal.js framework.

## Community & Ecosystem

Special thanks to the broader Claude Code community for sharing patterns, best practices, and innovative approaches to AI-assisted development workflows.

## Contributing

If you believe your work has been used in a way that constitutes copyright infringement, or if you'd like to be added to this credits file, please open an issue or contact the maintainers.

---

**Last Updated:** January 2025
