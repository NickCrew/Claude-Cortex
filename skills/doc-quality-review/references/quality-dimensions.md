# Quality Dimensions — Detailed Scoring Rubrics

Detailed scoring criteria with examples for each score level. Load this reference
at the start of a quality review to calibrate scoring.

---

## Readability

### Score 5 — Excellent
> Install Cortex with pip:
>
> ```bash
> pip install cortex-cli
> ```
>
> This installs the `cortex` command and all required dependencies.

Short sentences. Active voice. One idea per paragraph. Technical terms used
appropriately for the audience.

### Score 3 — Adequate
> Installation of the Cortex tool can be performed by utilizing the pip package
> manager, which should be available in your Python environment. The command
> below will install it along with the required dependency set.

Nominalized verbs ("Installation... can be performed"). Unnecessary filler
("which should be available"). Passive construction. Still understandable
but requires more effort.

### Score 1 — Poor
> The installation process for the tool requires that the user ensure that
> their local development environment has been configured with the appropriate
> package management tooling (pip, in this case, though it should be noted that
> other package managers may or may not be supported at this time) prior to
> executing the installation command which will retrieve and install the
> package and its transitive dependency graph.

One 60-word sentence. Nested parentheticals. Passive voice throughout.
Reader loses track of what to actually do.

---

## Consistency

### Score 5 — Excellent
Every page uses:
- Same term for the same concept ("skill" everywhere, never "capability" or "module")
- ATX headers with sentence case
- Fenced code blocks with language tags
- Admonitions with `{: .note }` / `{: .warning }` syntax
- Imperative mood for instructions

### Score 3 — Adequate
- "config" in some places, "configuration" in others
- Most code blocks have language tags but a few don't
- Heading capitalization mixed (some title case, some sentence case)
- Instructions alternate between imperative ("Run this") and descriptive ("You can run this")

### Score 1 — Poor
- Same feature called "hooks", "automations", and "triggers" in different docs
- Some pages use `>` blockquotes for notes, others use `{: .note }`, others use bold text
- No consistent heading hierarchy — some pages jump from `#` to `###`
- Mix of British and American spelling

---

## Audience Fit

### Score 5 — Excellent

**For a new user doc:**
> **Prerequisites:** Python 3.9+ installed. No prior experience with Cortex needed.
>
> In this tutorial, you'll install Cortex and create your first configuration.
> By the end, you'll have a working setup that...

States exactly what the reader needs to know. Sets expectations. Doesn't assume
product knowledge.

### Score 3 — Adequate

**For a new user doc:**
> Let's get Cortex set up. Run `cortex init` and then configure your scopes.

Assumes the reader knows what "scopes" are. Jumps to a command without explaining
what it does. Experienced users would be fine; new users are lost.

### Score 1 — Poor

**For a new user doc:**
> Configure the CLAUDE_PLUGIN_ROOT to point to your local checkout. Ensure
> .active-agents state files are not committed. Front matter parsing uses
> _tokenize_front_matter() — see core/base.py for edge cases.

Developer internals in a user-facing doc. References code paths. Assumes deep
familiarity with the codebase.

---

## Structure & Scannability

### Score 5 — Excellent
- Clear heading hierarchy visible in sidebar/TOC
- Each section starts with a one-line summary
- Reference data in tables, not prose
- Code examples immediately follow the concept they illustrate
- Long page has a "Summary" or "Quick Reference" at the top

### Score 3 — Adequate
- Headings exist but some sections are 500+ words without subheadings
- Some reference data buried in prose paragraphs
- Code examples present but not consistently placed
- No summary — reader must read linearly

### Score 1 — Poor
- Single heading, then wall of text
- No tables — everything in paragraph form including lists of options
- Code examples separated from the concepts they demonstrate
- Reader must read the entire page to find one flag's default value

---

## Actionability

### Score 5 — Excellent
> ## Add a New Skill
>
> 1. Create the skill directory:
>    ```bash
>    mkdir -p skills/my-skill/references
>    ```
>
> 2. Create `SKILL.md` with this template:
>    ```markdown
>    ---
>    name: my-skill
>    description: What this skill does
>    ---
>    # My Skill
>    ```
>
> 3. Test that Cortex discovers it:
>    ```bash
>    cortex skills list | grep my-skill
>    ```
>    Expected output: `my-skill  What this skill does`

Every step has a command. Expected output shown. Reader can verify success.

### Score 3 — Adequate
> To add a skill, create a directory in `skills/` with a `SKILL.md` file.
> The file should have YAML front matter with name and description fields.
> Then check that Cortex can find it.

Tells the reader what to do but not exactly how. No commands to copy-paste.
No expected output. Reader has to figure out the details.

### Score 1 — Poor
> Skills are extensible components that can be added to the framework.
> The system discovers them via the skills directory structure and
> metadata parsing subsystem.

Describes the system but gives the reader no path to action. After reading,
they know *about* skills but can't add one.

---

## Flagging Thresholds

When reviewing, flag findings at these thresholds:

| Metric | Flag when |
|--------|-----------|
| Sentence length | >30 words |
| Paragraph length | >6 sentences |
| Passive voice density | >40% of sentences in a section |
| Undefined jargon | Technical term used before definition |
| Section length | >500 words without a subheading |
| Code example | Missing imports, incomplete, or wouldn't run |
| Ambiguous pronoun | "it", "this", "that" without clear referent within 1 sentence |
| Missing prerequisite | Instruction assumes knowledge not established in this doc or stated as prerequisite |
