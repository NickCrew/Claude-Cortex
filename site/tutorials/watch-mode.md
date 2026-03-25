---
layout: default
title: Watch Mode Setup and Use
parent: Tutorials
nav_order: 6
---

# Watch Mode Setup and Use

This tutorial shows how to bring `cortex ai watch` into your daily workflow
without turning it into background noise.

Watch mode is most useful when you want Cortex to notice changes as your task
evolves and keep surfacing:

- high-confidence agent recommendations
- skill suggestions tied to current file and repo context

The important part is learning when to start safe, when to tune it, and when to
leave it off.

## What You'll Learn

- how to start watch mode in the foreground
- how to use daemon mode when you want it running in the background
- how `--threshold`, `--interval`, and `--no-auto-activate` change the feel of
  the system
- when watch mode is helpful versus when it becomes noisy

## Prerequisites

- Cortex installed locally
- a git-backed repository where changes are actively happening

## Time Estimate

~15-20 minutes

---

## What Watch Mode Actually Does

`cortex ai watch` monitors your current working context and continuously checks
for recommendation signals.

In practice it can surface:

- agent recommendations from the AI intelligence system
- skill suggestions tied to the same evolving context

That means watch mode is not just "run `cortex ai recommend` once." It is the
continuous version of that recommendation loop.

## Step 1: Start in the Foreground, Safely

For a first session, avoid automatic activation:

```bash
cortex ai watch --no-auto-activate
```

This is the best way to learn what watch mode is doing without letting it take
action yet.

If you are comfortable with the defaults and want the full behavior:

```bash
cortex ai watch
```

### Why start this way

Foreground mode gives you immediate feedback about:

- what context Cortex is detecting
- how often recommendations appear
- whether the current repo is a good candidate for continuous watching

## Step 2: Understand the Defaults

The default behavior is:

- threshold: `0.7`
- interval: `2.0` seconds
- auto-activate: enabled unless you pass `--no-auto-activate`

Those defaults are good enough to start, but not always good enough to keep.

## Step 3: Tune the Threshold

The threshold controls how confident Cortex must be before it surfaces a
recommendation.

Raise it if watch mode feels noisy:

```bash
cortex ai watch --no-auto-activate --threshold 0.8
```

Lower it if you want more sensitivity:

```bash
cortex ai watch --no-auto-activate --threshold 0.6
```

### Rule of thumb

- use a **higher** threshold when the repo has lots of unrelated churn
- use a **lower** threshold when you want earlier hints during exploratory work

If you are unsure, stay close to `0.7` and change only one variable at a time.

## Step 4: Tune the Interval

The interval controls how often watch mode checks for changes.

Slow it down if the repo is busy or you want less chatter:

```bash
cortex ai watch --no-auto-activate --interval 5
```

Speed it up if you want faster feedback:

```bash
cortex ai watch --no-auto-activate --interval 1.5
```

The right setting depends on how quickly your task context is changing and how
much feedback you actually want to read.

## Step 5: Limit the Watch Scope

If you do not want to watch everything, point it at specific directories:

```bash
cortex ai watch --dir src
cortex ai watch --dir src --dir tests
```

This is often better than lowering the threshold endlessly. If the signal is
coming from too much unrelated code, reduce the scope instead of only tuning
confidence.

## Step 6: Move to Daemon Mode

Once the behavior feels useful, you can move it into the background:

```bash
cortex ai watch --daemon
```

Check whether the daemon is running:

```bash
cortex ai watch --status
```

Stop it when you are done:

```bash
cortex ai watch --stop
```

If you want a custom daemon log file:

```bash
cortex ai watch --daemon --log ~/tmp/cortex-watch.log
```

Daemon mode is best when:

- you already trust the settings
- you want watch mode to stay available across a longer work session
- you do not want it occupying the foreground terminal

## Step 7: Know When Auto-Activation Helps

Auto-activation is useful when:

- the task is moving through clearly detectable contexts
- you already trust the recommendations
- you want Cortex to keep up without extra manual steps

It is less useful when:

- you are still exploring
- the repo is noisy
- you want to review every recommendation before taking action

That is why `--no-auto-activate` is the best starting point for most first
sessions.

## When Watch Mode Is Helpful

Use watch mode when:

- your task is evolving over time
- files are changing across several related areas
- you want recommendations to keep updating without rerunning commands manually

Good examples:

- feature work that spans frontend, API, and tests
- long debugging sessions where the context changes as you narrow the cause
- refactors that touch multiple directories over time

## When Watch Mode Becomes Noisy

Watch mode is a bad fit when:

- the repo has lots of unrelated churn
- you are not actively changing files
- you only need a single one-time recommendation

In those cases, prefer:

```bash
cortex ai recommend
```

That gives you a point-in-time recommendation without the overhead of a running
watch loop.

## Suggested First Watch-Mode Loop

Start with this:

```text
1. cortex ai watch --no-auto-activate
2. observe whether the recommendations feel useful
3. raise threshold if it is noisy
4. narrow --dir if the repo scope is too broad
5. move to --daemon only after the behavior feels right
```

That sequence makes watch mode much easier to trust.

## Summary

The best watch-mode workflow is:

1. start in the foreground
2. disable auto-activation at first
3. tune threshold before chasing every recommendation
4. tune interval and directory scope if the signal is noisy
5. move to daemon mode only once it earns its place in the session

## Related

- [AI Intelligence]({% link guides/ai-intelligence.md %}) -- deeper guide to recommendation behavior and watch-mode defaults
- [Feature Workflow in Cortex]({% link tutorials/feature-workflow.md %}) -- use watch mode during multi-step feature work
- [Bug Fix Workflow in Cortex]({% link tutorials/bug-fix-workflow.md %}) -- use watch mode during longer debugging sessions
