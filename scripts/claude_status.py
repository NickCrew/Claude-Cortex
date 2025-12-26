#!/usr/bin/env python3
"""Claude Code status line - Powerlevel10k lean theme inspired."""

from __future__ import annotations

import sys
from pathlib import Path

# Add repository root to path for imports when running from source.
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_ctx_py.statusline import main


if __name__ == "__main__":  # pragma: no cover - script wrapper
    raise SystemExit(main())
