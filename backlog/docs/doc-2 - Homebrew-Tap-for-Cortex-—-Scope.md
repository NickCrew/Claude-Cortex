---
id: doc-2
title: Homebrew Tap for Cortex — Scope
type: other
created_date: '2026-04-19 06:06'
---
# Homebrew Tap for Cortex — Scope

**Status:** Proposed
**Created:** 2026-04-19
**Depends on:** PyPI release pipeline (exists), manpage generation (exists), `cortex completions` subcommand (missing), skills/schemas install flow (done this session)

## Goals

Ship Cortex as a Homebrew-installable tool so that users can:

```bash
brew tap nickcrew/cortex
brew install cortex
```

…and end up with:

- `cortex` binary on PATH
- Shell completions registered (bash/zsh/fish)
- Manpages installed
- Skills/agents/rules/schemas symlinked into `~/.claude` via the install
- Automatic propagation of future releases via `brew update && brew upgrade`

**Non-goals** (separate workstreams):

- Windows packaging (winget/scoop/chocolatey) — parallel fate, different concerns
- Linuxbrew-specific tweaks — supported as a byproduct but not the primary target
- apt/yum/rpm packages — would need a different packaging stack entirely
- Docker images — user story is "install locally", not "run in container"

## Why a tap and not core Homebrew

Getting into `homebrew-core` requires upstream review, stable API, ≥75 github stars, and a track record. Ships faster via a tap we control, and we can move upstream later if adoption justifies it.

## Prerequisites (must land before the tap)

1. **`cortex completions {bash,zsh,fish}` subcommand**
   - Prints the shell completion script to stdout
   - Homebrew's `generate_completions_from_executable` helper invokes this at build time
   - Implementation: `argparse`-based completion is well-supported via `argcomplete` (already a dep — see `.venv/bin/activate-global-python-argcomplete`). Wire it behind a new CLI subcommand.

2. **Manpage validation**
   - `pyproject.toml` already declares manpages in `[tool.setuptools.data-files]` under `share/man/man1/`
   - Verify they install correctly from a wheel (spot-check after `pip install dist/*.whl`)
   - No work needed if the existing pipeline is healthy; audit only

3. **Stable PyPI release flow**
   - Tap formula downloads from PyPI (sdist) or GitHub release tarball
   - Need a `cortex X.Y.Z` tag per release, matching a published wheel/sdist
   - `semantic-release.yml` workflow exists — verify it publishes to PyPI, not just tags git

4. **`~/.claude` install flow on first run**
   - `cortex install link` already symlinks agents/skills/rules/schemas (as of commit `259d3d7`)
   - The formula's `post_install` calls this so the user doesn't have to

## Tap repository structure

```
homebrew-cortex/
├── Formula/
│   └── cortex.rb               # the formula
├── .github/
│   └── workflows/
│       ├── tests.yml           # brew test-bot on PRs
│       └── autobump.yml        # watches PyPI, opens bump PRs
└── README.md
```

Name convention: tap repo is `homebrew-cortex`, formula is `cortex.rb`, user invocation is `brew tap <owner>/cortex`.

## Formula sketch

```ruby
class Cortex < Formula
  include Language::Python::Virtualenv

  desc "Claude Code context and skill orchestration CLI"
  homepage "https://github.com/NickCrew/claude-cortex"
  url "https://files.pythonhosted.org/packages/.../claude-cortex-X.Y.Z.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "python@3.12"

  # Generated via `brew update-python-resources cortex` from pyproject.toml:
  resource "pyyaml" do ... end
  resource "jsonschema" do ... end
  # ...all transitive deps vendored here

  def install
    virtualenv_install_with_resources

    # Shell completions — requires `cortex completions <shell>` subcommand
    generate_completions_from_executable(bin/"cortex", "completions")

    # Manpages — pre-built in the sdist under share/man/man1/
    man1.install Dir["share/man/man1/*.1"]
  end

  def post_install
    # One-time link of shipped assets into ~/.claude
    system bin/"cortex", "install", "link"
  end

  test do
    system bin/"cortex", "--version"
  end
end
```

## Phases

### Phase 1 — `cortex completions` subcommand (~half-day)

- Add `cortex completions {bash,zsh,fish}` that prints the completion script
- Wire via `argcomplete.shellcode` or a custom template
- Test each shell end-to-end: `source <(cortex completions zsh)` and tab-complete a cortex subcommand
- Unit test: `cortex completions bash | grep -q '_cortex'`

### Phase 2 — PyPI release dry-run (~half-day)

- Run the existing `semantic-release.yml` workflow end-to-end in a staging/test PyPI environment, or verify the last release actually landed
- Confirm the sdist contains `share/man/man1/*.1` manpages and `skills/`, `agents/`, `rules/`, `schemas/` asset directories
- `pip install <sdist>` into a clean venv, confirm `cortex --version` and `cortex install link` both work

### Phase 3 — Formula authoring (~1 day)

- Create `nickcrew/homebrew-cortex` GitHub repo
- Generate `Formula/cortex.rb` based on the template above
- Run `brew update-python-resources cortex` to vendor dep resources
- Local test: `brew install --build-from-source ./Formula/cortex.rb`
- Iterate on any dep resolution issues

### Phase 4 — CI + release automation (~1 day)

- `tests.yml` — runs `brew test-bot` on PRs, validates formula syntax + install + test block
- `autobump.yml` — cron workflow that polls PyPI for new versions, opens a PR bumping `url`/`sha256`/any new resources. Existing action: `dawidd6/action-homebrew-bump-formula` or a custom script
- Documented: when a new Cortex version is released on PyPI, a PR auto-opens in the tap repo within a few hours

### Phase 5 — Documentation + onboarding (~half-day)

- `README.md` in the tap repo: install instructions, troubleshooting
- Main repo's install docs link to the tap as a macOS-preferred path
- Announce in `CHANGELOG.md`

## Open questions

1. **Tap name.** `nickcrew/homebrew-cortex`, `NickCrew/homebrew-cortex`, or something under an org? Affects `brew tap <owner>/cortex`.
2. **Python version pin.** `python@3.12` matches CI; `python@3.13` is available. Consider whether deps are compatible with the latest.
3. **`cortex install link` as post_install:** runs automatically on first install, but what if the user already has a working `~/.claude` from a repo-clone-based install? The link step is idempotent (my Phase 4 schemas work confirmed this), but worth adding a `--skip-link` env var escape hatch.
4. **Update posture.** Do we want users on the latest auto (`brew upgrade`), or pin? Tap users expect the former.
5. **Reverse migration.** If a user installs via pip, then later via brew, they'd have two `cortex` binaries. Document precedence (brew wins if its bin is earlier in PATH).

## Risks

- **Python-on-Homebrew is finicky.** Dep vendoring via `brew update-python-resources` can break on complex dep trees; semantic_version / fastembed / sqlite3 extras might need special handling.
- **Manpage dependency.** If the manpage build is broken, `man1.install` fails silently or loudly. Audit first.
- **Formula review cost.** Even for a personal tap, keeping formulas green requires occasional CI babysitting.
- **Windows gap.** Even after Homebrew is done, Windows users still need a story. Won't be this workstream, but worth communicating.

## Suggested rollout order

1. Phase 1 (completions) — useful standalone, unblocks tap
2. Phase 2 (release verification) — catches packaging issues before tap authoring
3. Phase 3 (formula) — the actual tap
4. Phase 4 (automation) — only after Phase 3 is stable
5. Phase 5 (docs) — last, once users actually have a tap to read about

Phases 1-2 can proceed even without committing to the full tap — they're useful on their own.

## Success criteria

- A new macOS user can `brew tap <owner>/cortex && brew install cortex` and immediately run `cortex skills list` with shell completions working
- `brew upgrade cortex` picks up new PyPI releases without manual intervention
- The tap repo has a green CI status badge
- Zero reports of "broken install" in the first week post-launch
