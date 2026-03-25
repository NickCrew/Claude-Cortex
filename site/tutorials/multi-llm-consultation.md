---
layout: default
title: Multi-LLM Consultation Workflow
parent: Tutorials
nav_order: 7
---

# Multi-LLM Consultation Workflow

This tutorial shows how to use exported Cortex context with the
`multi-llm-consult` workflow to get a second opinion, sanity-check a plan, or
delegate a narrow analysis to another model.

The goal is not to replace your main session. The goal is to ask another model
one bounded question, then bring the answer back into your real workflow.

## What You'll Learn

- how to prepare a safe, focused consultation request
- how to export only the context another model actually needs
- how to run the `multi-llm-consult` script with the right purpose
- how to treat external model output as advisory and fold it back into your
  main decision-making

## Prerequisites

- Cortex installed locally
- at least one provider configured in the TUI
- a concrete task where you want another model's opinion

## Time Estimate

~15-20 minutes

---

## Scenario

Assume you already have a direction in mind, but you want help with one of
these questions:

- "What risks am I missing?"
- "Is this implementation plan sound?"
- "Can another model review this handoff bundle before I act?"
- "Can I delegate one narrow analysis task while I keep moving?"

That is the right shape for `multi-llm-consult`.

## Step 1: Configure a Provider

The easiest way to configure providers is through the TUI:

1. Run `cortex tui`
2. Press `Ctrl+P` to open the Command Palette
3. Run `Configure LLM Providers`
4. Set API keys for the provider you want to use

The supported provider names in the consult script are:

- `openai`
- `codex`
- `gemini`
- `qwen`

Provider settings are stored under `llm_providers` in your Claude
`settings.json`.

## Step 2: Choose a Single Purpose

Do not ask another model to "analyze everything." Pick one purpose:

- `second-opinion`
- `plan`
- `review`
- `delegate`

This keeps the consult request narrow enough to compare against reality later.

Good examples:

- "Review this refactor plan and list the top three risks."
- "Check whether this bug-fix approach is missing edge cases."
- "Compare two implementation options and recommend one."

## Step 3: Export a Small Context Bundle

Most consult requests do not need your whole repo. Start with a minimal export:

```bash
cortex export context /tmp/consult-context.md --include core --include skills
```

If the skill shortlist matters, capture that too:

```bash
cortex skills context --no-write > /tmp/consult-skills.md
```

If the export still feels noisy, trim it before sending anything out:

```bash
cortex export context /tmp/consult-context.md \
  --include core \
  --include skills \
  --exclude-file rules/quality-rules.md
```

The safest default is still: send less.

## Step 4: Write the Consult Prompt

Put the actual question in a small prompt file so the request stays explicit:

```markdown
# Purpose
review

# Task
Review this proposed bug-fix workflow and point out the top three technical
risks or missing checks.

# Constraints
- Stay within the current Cortex CLI and skill model
- Treat the attached context as partial, not authoritative
- Prefer concise, actionable feedback
```

Save that as `/tmp/consult-prompt.md`.

Before sending anything to an external provider:

- remove secrets
- remove credentials or tokens
- remove unrelated private data
- avoid dumping files just because they are available

## Step 5: Run the Consultation

The consult script lives with the skill:

```bash
python3 skills/multi-llm-consult/scripts/consult_llm.py --help
```

A review-oriented consult looks like this:

```bash
python3 skills/multi-llm-consult/scripts/consult_llm.py \
  --provider gemini \
  --purpose review \
  --prompt-file /tmp/consult-prompt.md \
  --context-file /tmp/consult-context.md \
  --show-metadata
```

A plan check against Codex looks like this:

```bash
python3 skills/multi-llm-consult/scripts/consult_llm.py \
  --provider codex \
  --purpose plan \
  --prompt-file /tmp/consult-prompt.md \
  --context-file /tmp/consult-context.md
```

If you want to delegate a narrow analysis task:

```bash
python3 skills/multi-llm-consult/scripts/consult_llm.py \
  --provider qwen \
  --purpose delegate \
  --prompt-file /tmp/consult-prompt.md \
  --context-file /tmp/consult-context.md
```

## Step 6: Treat the Answer as Advisory

This is the most important step.

Do not paste the answer back into your workflow as if it were settled fact.
Instead:

1. summarize the response in 3-6 bullets
2. separate observations from recommendations
3. compare the claims against the current repo and CLI surface
4. decide what actually changes in your plan

Useful questions to ask yourself:

- Did the other model identify a real risk I had missed?
- Did it assume a command, flag, or file that does not actually exist here?
- Does its advice fit the current Cortex workflow, or is it generic?

## Step 7: Feed It Back into the Main Session

Once you have a cleaned-up summary, fold it back into your real workflow.

Typical patterns:

- update your implementation plan
- run a narrower `cortex skills recommend` pass
- export a revised context bundle
- ask for a second consult from a different provider
- move forward and explicitly ignore low-value suggestions

The important part is that your main session stays in charge.

## Safe Defaults

If you are unsure, use this pattern:

1. configure one provider in the TUI
2. export only `core` and `skills`
3. write a prompt file with one purpose
4. run one consult
5. summarize the answer before changing anything

That keeps the consultation useful without turning it into a side quest.

## Summary

The workflow is:

1. choose a bounded consult purpose
2. export a small context bundle
3. sanitize the request
4. run the consult script with one provider
5. interpret the result as advisory
6. feed the useful parts back into your main Cortex session

That is what makes `multi-llm-consult` valuable: it gives you another
perspective without giving up control of the main workflow.

## Related

- [Export Context for Handoffs]({% link tutorials/export-context.md %}) -- build tighter context bundles for outside consultation
- [Skills to Context Handoff]({% link tutorials/skill-recommendations.md %}) -- generate the skill context you may want to include
- [Multi-LLM Consult]({% link guides/llm-consult.md %}) -- reference guide to the consult workflow
