"""Integration test ensuring CLI entry calls TUI launcher."""

from __future__ import annotations

import pytest
import sys
import types

from claude_ctx_py import cli


@pytest.mark.integration
def test_tui_entrypoint_invokes_main(monkeypatch: pytest.MonkeyPatch, capsys, test_project):
    called = {}

    def fake_tui_main():
        called["ran"] = True
        return 0

    # Stub the claude_ctx_py.tui module to avoid importing textual
    fake_module = types.SimpleNamespace(main=fake_tui_main)
    monkeypatch.setitem(sys.modules, "claude_ctx_py.tui", fake_module)

    code = cli.main(["tui"])
    output = capsys.readouterr().out

    assert code == 0
    assert called.get("ran") is True
    # CLI prints nothing for tui; ensure no stderr from parser
    assert "usage:" not in output
