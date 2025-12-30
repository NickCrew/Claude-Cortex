"""LLM provider settings dialog."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from ...core.hooks import load_settings, save_settings


@dataclass(frozen=True)
class ProviderSpec:
    key: str
    title: str
    env_var: str
    description: str


PROVIDERS: List[ProviderSpec] = [
    ProviderSpec(
        key="openai",
        title="OpenAI / Codex",
        env_var="OPENAI_API_KEY",
        description="Use for Codex or OpenAI-compatible models.",
    ),
    ProviderSpec(
        key="gemini",
        title="Gemini",
        env_var="GEMINI_API_KEY",
        description="Google Gemini API key.",
    ),
    ProviderSpec(
        key="qwen",
        title="Qwen (DashScope)",
        env_var="DASHSCOPE_API_KEY",
        description="Alibaba DashScope API key for Qwen models.",
    ),
]


class LLMProviderSettingsDialog(ModalScreen[bool]):
    """Dialog for configuring external LLM provider keys."""

    CSS = """
    LLMProviderSettingsDialog {
        align: center middle;
    }

    LLMProviderSettingsDialog #dialog {
        width: 85%;
        max-width: 100;
        height: 85%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 1;
    }

    LLMProviderSettingsDialog #dialog-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    LLMProviderSettingsDialog #providers-container {
        height: 1fr;
        border: solid $primary-darken-2;
        background: $surface;
        padding: 1;
    }

    LLMProviderSettingsDialog .provider-title {
        text-style: bold;
        color: $primary;
        margin-top: 1;
    }

    LLMProviderSettingsDialog .provider-desc {
        color: $text-muted;
        margin-bottom: 1;
    }

    LLMProviderSettingsDialog #dialog-buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    LLMProviderSettingsDialog #dialog-buttons Button {
        margin: 0 1;
    }

    LLMProviderSettingsDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }

    LLMProviderSettingsDialog #dialog-error {
        text-align: center;
        color: $error;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.settings: Dict[str, Any] = load_settings()
        raw_providers = self.settings.get("llm_providers", {})
        self.provider_settings: Dict[str, Any] = (
            raw_providers if isinstance(raw_providers, dict) else {}
        )
        self.error_message = ""

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("LLM Provider Keys", id="dialog-title")

            with VerticalScroll(id="providers-container"):
                for provider in PROVIDERS:
                    yield Label(provider.title, classes="provider-title")
                    current = self._current_status(provider)
                    env_hint = (
                        f"{provider.env_var} set"
                        if os.environ.get(provider.env_var)
                        else "env not set"
                    )
                    yield Static(
                        f"[dim]Current: {current} | {env_hint}[/dim]",
                        classes="provider-desc",
                    )
                    yield Static(provider.description, classes="provider-desc")
                    yield Input(
                        placeholder="Enter new API key (leave blank to keep current)",
                        password=True,
                        id=f"key-{provider.key}",
                    )

            yield Static(
                "[dim]Ctrl+S Save • Esc Cancel[/dim]",
                id="dialog-hint",
            )
            yield Static("", id="dialog-error")

            with Container(id="dialog-buttons"):
                yield Button("Save", variant="success", id="save")
                yield Button("Cancel", variant="default", id="cancel")

    def _current_status(self, provider: ProviderSpec) -> str:
        entry = self.provider_settings.get(provider.key, {})
        if isinstance(entry, dict) and entry.get("api_key"):
            return "stored"
        if os.environ.get(provider.env_var):
            return "env"
        return "not set"

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_save()
        else:
            self.action_cancel()

    def action_save(self) -> None:
        updated = False
        for provider in PROVIDERS:
            try:
                input_widget = self.query_one(f"#key-{provider.key}", Input)
            except Exception:
                continue
            value = input_widget.value.strip()
            if not value:
                continue
            entry = self.provider_settings.get(provider.key)
            if not isinstance(entry, dict):
                entry = {}
            entry["api_key"] = value
            self.provider_settings[provider.key] = entry
            updated = True

        if updated:
            self.settings["llm_providers"] = self.provider_settings
            success, message = save_settings(self.settings)
            if not success:
                self.error_message = message
                try:
                    self.query_one("#dialog-error", Static).update(message)
                except Exception:
                    pass
                return

        self.dismiss(True)
