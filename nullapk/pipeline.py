"""Orchestrates the parse -> token -> download workflow shared by the CLI and TUI front ends."""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from nullapk import dispenser, downloader, playstore
from nullapk.errors import NullApkError

DEFAULT_OUTPUT_DIR = Path.home() / "Desktop" / "nullapk" / "apk"


class Step(Enum):
    PARSE = auto()
    REQUEST_TOKEN = auto()
    DOWNLOAD = auto()
    DONE = auto()


@dataclass(frozen=True)
class StepUpdate:
    step: Step
    message: str


ProgressCallback = Callable[[StepUpdate], None]


def _noop(_: StepUpdate) -> None:
    return None


def run(target: str, output_dir: Path = DEFAULT_OUTPUT_DIR, on_progress: ProgressCallback = _noop) -> Path:
    """Run the full pipeline, saving as `<output_dir>/<package_id>.apk`. Raises NullApkError on failure."""
    on_progress(StepUpdate(Step.PARSE, f"Parsing target: {target}"))
    package_id = playstore.extract_package_id(target)
    on_progress(StepUpdate(Step.PARSE, f"Resolved package id: {package_id}"))

    on_progress(StepUpdate(Step.REQUEST_TOKEN, "Requesting anonymous auth token from Aurora dispenser..."))
    token = dispenser.fetch_token()
    on_progress(StepUpdate(Step.REQUEST_TOKEN, f"Token issued for pooled account {token.email}"))

    dest_file = Path(output_dir) / f"{package_id}.apk"
    on_progress(StepUpdate(Step.DOWNLOAD, f"Downloading {package_id} via apkeep..."))
    saved_path = downloader.download(package_id, token, dest_file)
    on_progress(StepUpdate(Step.DOWNLOAD, f"Saved to {saved_path}"))
    on_progress(StepUpdate(Step.DONE, str(saved_path)))

    return saved_path


__all__ = ["run", "Step", "StepUpdate", "ProgressCallback", "DEFAULT_OUTPUT_DIR", "NullApkError"]
