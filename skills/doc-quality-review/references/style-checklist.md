# Style Checklist

Concrete rules for the most common documentation quality issues. Use during Phase 2
to identify specific findings.

---

## Prose

- [ ] **Active voice.** "Cortex discovers skills" not "Skills are discovered by Cortex"
- [ ] **Imperative for instructions.** "Run the command" not "You should run the command"
- [ ] **Present tense for descriptions.** "The CLI reads config from..." not "The CLI will read..."
- [ ] **Concrete subjects.** "The parser extracts..." not "It extracts..." (unless referent is obvious)
- [ ] **No nominalizations.** "Install" not "Perform an installation"
- [ ] **No hedge stacking.** "This might possibly help to potentially..." — pick one qualifier or none

## Structure

- [ ] **One topic per page.** If a page covers two unrelated features, split it
- [ ] **Front-load key info.** The first sentence of a section should be its most important point
- [ ] **Heading hierarchy.** `##` before `###` before `####` — no skipping levels
- [ ] **Sentence case headings.** "Getting started" not "Getting Started" (unless project convention differs)
- [ ] **Parallel structure in lists.** All items start with the same part of speech

## Code Examples

- [ ] **Language tag on every fenced block.** ` ```bash ` not ` ``` `
- [ ] **Copy-pasteable.** Reader shouldn't need to edit the example to run it
- [ ] **Show output for non-obvious commands.** What does success look like?
- [ ] **One concept per example.** Don't combine three features in one code block
- [ ] **No placeholder paths.** Use realistic paths or explicit `<placeholders>` with explanation

## Formatting

- [ ] **Tables for reference data.** If you're listing flags, options, or config keys, use a table
- [ ] **Consistent admonitions.** Use the project's callout convention (note/warning/tip), not bold text
- [ ] **No orphan links.** Every link should have context — why would the reader follow it?
- [ ] **Consistent list markers.** Bullets (`-`) for unordered, numbers for sequential steps

## Terminology

- [ ] **One term per concept.** Don't alternate between synonyms ("config" / "configuration" / "settings")
- [ ] **Define on first use.** Technical terms get a brief definition or link the first time they appear
- [ ] **Match the UI.** If the product calls it "Skills", docs call it "Skills" — not "capabilities" or "modules"
- [ ] **No internal jargon in user docs.** "State file" vs ".active-agents file" — use what the user sees

## Common Mistakes to Flag

| Pattern | Problem | Fix |
|---------|---------|-----|
| "In order to" | Filler | "To" |
| "It should be noted that" | Filler | Delete, state the fact directly |
| "Basically" / "Simply" | Minimizes reader's difficulty | Delete |
| "As mentioned above/below" | Fragile reference | Link to the specific section |
| "Please" | Unnecessary in technical docs | Delete |
| "Obviously" / "Clearly" | Condescending if reader doesn't find it obvious | Delete |
| "etc." | Vague — reader doesn't know what else is included | List the items or say "and others" |
| "Note:" followed by paragraph | Often buries important info | Use an admonition callout, or if critical, put it in the main text |
