"""Wraps the `apkeep` binary to perform the actual Google Play download."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from nullapk.dispenser import AuthToken
from nullapk.errors import DownloadError, MissingDependencyError

APKEEP_BINARY = "apkeep"


def ensure_apkeep_available() -> None:
    if shutil.which(APKEEP_BINARY) is None:
        raise MissingDependencyError(
            f"'{APKEEP_BINARY}' was not found on PATH. Install it with: "
            "cargo install apkeep  (or see https://github.com/EFForg/apkeep)"
        )


def download(package_id: str, token: AuthToken, dest_file: Path) -> Path:
    ensure_apkeep_available()

    dest_file = Path(dest_file).expanduser()
    dest_file.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="nullapk-") as tmp:
        tmp_dir = Path(tmp)
        result = subprocess.run(
            [
                APKEEP_BINARY,
                "-a", package_id,
                "-d", "google-play",
                "-e", token.email,
                "--auth-token", token.auth_token,
                "--accept-tos",
                str(tmp_dir) + "/",
            ],
            capture_output=True,
            text=True,
        )

        downloaded = next(tmp_dir.glob("*.apk"), None)
        if result.returncode != 0 or downloaded is None:
            detail = (result.stdout + result.stderr).strip() or "no output"
            raise DownloadError(f"apkeep failed for '{package_id}': {detail}")

        shutil.move(str(downloaded), dest_file)

    return dest_file
