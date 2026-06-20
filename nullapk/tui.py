"""Textual front end: paste a Play Store link, press Download, watch it land on disk."""

from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Footer, Header, Input, LoadingIndicator, RichLog, Static

from nullapk import pipeline
from nullapk.errors import NullApkError

CSS_PATH = Path(__file__).with_name("tui.tcss")


class NullApkApp(App):
    CSS_PATH = CSS_PATH
    TITLE = "nullapk"
    BINDINGS = [("q", "quit", "Quit"), ("ctrl+c", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main"):
            yield Static("Google Play APK fetcher", id="title")
            yield Static("Play Store URL or package id:", classes="label")
            yield Input(
                placeholder="https://play.google.com/store/apps/details?id=com.example.app",
                id="target_input",
            )
            yield Button("Download", id="download_btn", variant="success")
            yield LoadingIndicator(id="loading", classes="hidden")
            yield RichLog(id="log", wrap=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#target_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download_btn":
            self._start_download()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._start_download()

    def _start_download(self) -> None:
        target = self.query_one("#target_input", Input).value.strip()
        log = self.query_one("#log", RichLog)

        if not target:
            log.write("[bold red]Enter a Play Store URL or package id first.[/]")
            return

        self._set_busy(True)
        log.clear()
        self._run_pipeline(target)

    def _set_busy(self, busy: bool) -> None:
        self.query_one("#download_btn", Button).disabled = busy
        self.query_one("#target_input", Input).disabled = busy
        loading = self.query_one("#loading", LoadingIndicator)
        loading.set_class(not busy, "hidden")

    @work(thread=True, exclusive=True)
    def _run_pipeline(self, target: str) -> None:
        log = self.query_one("#log", RichLog)

        def on_progress(update: pipeline.StepUpdate) -> None:
            self.call_from_thread(log.write, f"[cyan]•[/] {update.message}")

        try:
            saved_path = pipeline.run(target, on_progress=on_progress)
        except NullApkError as exc:
            self.call_from_thread(log.write, f"[bold red]Error:[/] {exc}")
            self.call_from_thread(
                self.notify, str(exc), title="Download failed", severity="error", timeout=10
            )
        except Exception as exc:  # noqa: BLE001 - surface unexpected failures in the UI, not a crash
            self.call_from_thread(log.write, f"[bold red]Unexpected error:[/] {exc}")
            self.call_from_thread(
                self.notify, str(exc), title="Unexpected error", severity="error", timeout=10
            )
        else:
            self.call_from_thread(log.write, f"[bold green]Done.[/] Saved to {saved_path}")
            self.call_from_thread(
                self.notify, str(saved_path), title="Download complete", severity="information", timeout=10
            )
        finally:
            self.call_from_thread(self._set_busy, False)


def run() -> None:
    NullApkApp().run()
