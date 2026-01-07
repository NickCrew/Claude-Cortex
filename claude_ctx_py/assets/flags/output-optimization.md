# Output Optimization Flags

Flags for controlling output verbosity and scope.

**Estimated tokens: ~120**

---

**--uc / --ultracompressed**
- Trigger: Context pressure, efficiency requirements, large operations
- Behavior: Symbol communication system, 30-50% token reduction
- Related: Reduces output verbosity while preserving clarity
- Uses: Emojis, abbreviations, structured formats
- Trade-off: Slight readability reduction for major token savings

**--scope [file|module|project|system]**
- Trigger: Analysis boundary needs, focused operations
- Behavior: Define operational scope and analysis depth
- Levels:
  - `file`: Single file operations only
  - `module`: Related files in same module/directory
  - `project`: Entire project codebase
  - `system`: Multi-project or cross-system analysis
- Impact: Limits search, analysis, and modification scope

**--focus [performance|security|quality|architecture|accessibility|testing]**
- Trigger: Domain-specific optimization needs
- Behavior: Target specific analysis domain and expertise application
- Domains:
  - `performance`: Speed, memory, scalability optimization
  - `security`: Vulnerability analysis, secure coding
  - `quality`: Code quality, maintainability, standards
  - `architecture`: System design, patterns, structure
  - `accessibility`: WCAG compliance, inclusive design
  - `testing`: Test coverage, quality, reliability
- Result: Deep analysis in chosen domain, surface-level elsewhere
