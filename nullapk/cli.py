"""Entry point: launches the TUI by default, or runs headless when a target is given."""

import argparse
import sys
from pathlib import Path

from rich.console import Console

from nullapk import pipeline
from nullapk.errors import NullApkError


def _run_headless(target: str, output_dir: Path) -> int:
    console = Console()

    def on_progress(update: pipeline.StepUpdate) -> None:
        console.print(f"[cyan]•[/] {update.message}")

    try:
        saved_path = pipeline.run(target, output_dir, on_progress=on_progress)
    except NullApkError as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        return 1

    console.print(f"[bold green]Done.[/] Saved to {saved_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="nullapk",
        description="Fetch a Google Play APK from a Play Store link via Aurora Store's dispenser.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Play Store URL or bare package id. Omit to launch the interactive TUI.",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=str(pipeline.DEFAULT_OUTPUT_DIR),
        help=f"Directory to save into; file is named <package-id>.apk (default: {pipeline.DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    if args.target is None:
        from nullapk.tui import run as run_tui
        run_tui()
        return

    sys.exit(_run_headless(args.target, Path(args.output_dir).expanduser()))


if __name__ == "__main__":
    main()
