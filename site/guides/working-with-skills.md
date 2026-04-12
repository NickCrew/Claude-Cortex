---
layout: default
title: Working with Skills
parent: Guides
nav_order: 4
---

# Working with Skills

Cortex ships with more than a hundred skills. That's enough that "just remember
the one you need" stops being a strategy. This page explains how the system is
meant to be used in practice: what happens on its own, what you can trigger by
hand, and how to help Cortex get better at picking the right ones.

If you want a command-by-command tour instead, see
[Skills]({% link guides/skills.md %}).

## The mental model

Think of skills as a library, not a checklist. You never load them all. At any
given moment, only a small handful are relevant to what you're doing, and that
set shifts as your task shifts. The job of the recommendation system is to
narrow the library down to that handful without you having to ask.

Cortex does this on two tracks that run in parallel:

- **A hook that fires on every prompt.** It reads your prompt text and the
  files you're changing, and surfaces a short suggestion list inline in the
  session. Low latency, always on, no command needed.
- **A CLI you drive yourself.** `cortex skills recommend` and related commands
  give you the same engine on demand, with more detail and the ability to
  write a context file for another session.

Most users never touch the CLI path for day-to-day work. The hook handles
90% of the value. The CLI is there when you want to be explicit.

## What happens automatically

When you type a prompt in Claude Code, the auto-suggester hook inspects:

- the text of your prompt
- the files you've touched in this session
- the file types and directories involved
- your git branch name and recent commits

It then picks the handful of skills most likely to apply and inserts them as
a suggestion line that Claude can act on. You'll see something like:

```text
Suggested skills: agent-loops, systematic-debugging, git-ops
```

The hook is registered in `~/.claude/settings.json`. The easiest way to
install it is from the TUI:

```bash
cortex tui
```

Press `7` to open the Hooks view, select **skill_auto_suggester** from the
available hooks, and install it. The TUI writes the settings.json entry for
you and confirms the install. Once it's in place you don't need to activate
it per-session. If the hook ever goes quiet, that's usually a sign of a
missing optional dependency rather than a broken hook -- see
[Troubleshooting](#troubleshooting) below.

## What you can do on purpose

Three commands cover the CLI side. You don't need to memorize them, but they're
worth knowing exist:

```bash
cortex skills recommend            # shortlist for the current context
cortex skills context              # writes a handoff file for another session
cortex skills feedback <name> helpful   # tells the system a suggestion worked
```

The first two are identical to what the hook does internally -- they just give
you the answer directly so you can inspect, pipe, or share it. The third is
how you close the loop, which matters more than it sounds like it does.

## How the recommender decides

You don't need the internals to use Cortex effectively, but knowing roughly
what the system looks at makes it much easier to debug when a suggestion feels
wrong.

The recommender combines four different signals and merges them into a single
confidence score:

1. **Semantic similarity.** Your prompt and file context are compared against
   a memory of past sessions that worked well. The closer the match, the more
   weight the skills from those sessions get.
2. **File-pattern rules.** Certain paths and extensions map directly to
   skills -- editing a migration file surfaces database skills, editing a
   React component surfaces frontend skills.
3. **Agent associations.** If you have an agent active, skills that pair well
   with that agent get a boost.
4. **Historical success.** Skills that you've previously marked helpful for
   similar contexts get weighted up.

When multiple signals agree, confidence climbs fast. When only one signal
fires, the suggestion has to earn its place on its own. This is why the
system feels sharper in repos you've been working in for a while -- the
historical-success signal only exists once you've taught it something.

## Helping Cortex learn

This is the part most people skip, and it's also the part that makes the
biggest difference over time.

Every time you use a suggested skill and it actually helps, tell Cortex:

```bash
cortex skills feedback systematic-debugging helpful
```

Every time a suggestion lands wrong:

```bash
cortex skills feedback systematic-debugging not-helpful
```

Feedback goes into two places. It updates the per-skill success rate that
feeds future confidence scores, and it writes the current context into the
semantic memory so sessions with similar shapes pull the same skills next
time. After a week or two of honest feedback in a given repo, you should
notice suggestions getting noticeably more specific to your work.

Two things are worth knowing:

- **Feedback is per-recommendation, ratings are per-skill.** Use feedback
  ("did this suggestion help right now?") to teach the recommender. Use
  `cortex skills rate` for long-term quality judgments about the skill
  itself, independent of any single moment.
- **Negative feedback is just as valuable as positive.** The recommender
  uses both to shape its decisions. A skill you mark not-helpful three times
  in similar contexts will stop appearing there.

## Getting real value from a large library

If you've just installed Cortex and you're staring down a catalog of more
than a hundred skills, here's the practical advice:

1. **Don't browse the catalog.** It won't help. Skills are discovery-on-demand
   by design -- you'll meet them when they become relevant.
2. **Trust the hook for a few days.** Let it suggest things and follow its
   picks. You'll build intuition for which suggestions are worth taking.
3. **Rate things honestly as you go.** Even three or four feedback signals
   per day noticeably sharpens the recommender within a week.
4. **Run `cortex skills recommend` explicitly when you're stuck.** When you
   know the current task is unusual and the hook hasn't surfaced anything
   obvious, the CLI can give you a longer list to scan.
5. **Write your own skills for workflows you repeat.** The catalog is a
   starting point, not a ceiling. If you keep explaining the same thing to
   Cortex, that's a skill waiting to be authored --
   see [Skill Authoring]({% link tutorials/skill-authoring.md %}).

## Troubleshooting

**The hook stopped suggesting anything.** First, confirm the hook is
actually installed: open `cortex tui`, press `7` for the Hooks view, and
check that **skill_auto_suggester** appears under installed hooks. If it's
listed there but still silent, the most common cause is that the optional
`fastembed` dependency isn't installed in the active Python env, so the
semantic similarity layer returns no results. The other three signals still
work, but semantic-driven suggestions go quiet. Install it with
`pip install fastembed` and rerun.

**Suggestions feel too generic.** This usually means the historical-success
signal has nothing to draw on yet. Give feedback for a few days and the
suggestions should sharpen. If they don't, the prompt wording might be too
vague for the rules to catch -- try being slightly more specific.

**Suggestions feel too narrow.** The opposite problem: the file-pattern rules
are dominating and drowning out everything else. `cortex skills recommend`
shows a longer list than the hook does, so run it explicitly when you want a
broader view.

**I rated something wrong.** Rate it again with the opposite signal. The
system uses recent feedback, so corrections land quickly.

## Related

- [Skills]({% link guides/skills.md %}) -- command reference for `cortex skills`
- [Skill Authoring]({% link tutorials/skill-authoring.md %}) -- write your own
- [AI Intelligence]({% link guides/ai-intelligence.md %}) -- the agent-side story
- [Hooks]({% link guides/hooks.md %}) -- how the auto-suggester plugs in
