"""A Textual screen for viewing real-time command logs."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Footer, RichLog


class LogViewerScreen(Screen[None]):
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
        self._header_title = title
        self._process: Optional[asyncio.subprocess.Process] = None
        self._runner: Optional[asyncio.Task[None]] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header(show_clock=False)
        yield Container(RichLog(id="log-output", wrap=True, highlight=True), id="log-container")
        yield Footer()

    async def on_mount(self) -> None:
        """Start the subprocess and stream its output."""
        log = self.query_one(RichLog)
        if self.app is not None:
            self.app.title = self._header_title
        log.write(f"$ {' '.join(self.command)}\n")
        self._runner = asyncio.create_task(self._run_command(log))

    async def on_unmount(self) -> None:
        """Terminate the subprocess when the screen is closed."""
        if self._runner and not self._runner.done():
            self._runner.cancel()
            with suppress(asyncio.CancelledError):
                await self._runner
        self._runner = None

    async def _run_command(self, log: RichLog) -> None:
        try:
            self._process = await asyncio.create_subprocess_exec(
                *self.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            assert self._process.stdout is not None
            assert self._process.stderr is not None

            stdout_task = asyncio.create_task(
                self._read_stream(self._process.stdout, log)
            )
            stderr_task = asyncio.create_task(
                self._read_stream(self._process.stderr, log)
            )

            try:
                await asyncio.gather(stdout_task, stderr_task)
            finally:
                for task in (stdout_task, stderr_task):
                    if not task.done():
                        task.cancel()

            await self._process.wait()
            log.write(
                f"\n[bold green]Process finished with exit code {self._process.returncode}[/bold green]"
            )

        except asyncio.CancelledError:
            await self._terminate_process()
            raise
        except Exception as e:
            log.write(f"\n[bold red]Failed to start process: {e}[/bold red]")
        finally:
            self._process = None

    async def _terminate_process(self) -> None:
        if self._process and self._process.returncode is None:
            self._process.terminate()
            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(self._process.wait(), timeout=1.0)
            if self._process.returncode is None:
                self._process.kill()
                with suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(self._process.wait(), timeout=1.0)

    async def _read_stream(self, stream: asyncio.StreamReader | None, log: RichLog) -> None:
        """Read from a stream and write to the log widget."""
        if not stream:
            return
        while True:
            line = await stream.readline()
            if not line:
                break
            log.write(line.decode("utf-8"))
