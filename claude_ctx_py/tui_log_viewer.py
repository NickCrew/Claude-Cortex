"""A Textual screen for viewing real-time command logs."""

from __future__ import annotations

import asyncio
from typing import List

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Footer, RichLog


class LogViewerScreen(Screen):
    """A screen to display real-time output from a subprocess."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(
        self,
        command: List[str],
        *,
        title: str = "Log Viewer",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.command = command
        self.title = title

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header(self.title)
        yield Container(RichLog(id="log-output", wrap=True, highlight=True), id="log-container")
        yield Footer()

    async def on_mount(self) -> None:
        """Start the subprocess and stream its output."""
        log = self.query_one(RichLog)
        log.write(f"$ {' '.join(self.command)}\n")

        try:
            process = await asyncio.create_subprocess_exec(
                *self.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            await asyncio.gather(
                self._read_stream(process.stdout, log),
                self._read_stream(process.stderr, log)
            )

            await process.wait()
            log.write(f"\n[bold green]Process finished with exit code {process.returncode}[/bold green]")

        except Exception as e:
            log.write(f"\n[bold red]Failed to start process: {e}[/bold red]")

    async def _read_stream(self, stream: asyncio.StreamReader | None, log: RichLog) -> None:
        """Read from a stream and write to the log widget."""
        if not stream:
            return
        while True:
            line = await stream.readline()
            if not line:
                break
            log.write(line.decode("utf-8"))
