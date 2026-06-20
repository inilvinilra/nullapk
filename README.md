# nullapk

Fetch a Google Play APK straight from a Play Store link, no Play Store account or rooted device required.

```
nullapk
```

opens an interactive terminal UI: paste a Play Store URL (or a bare package id), hit **Download**, and the APK lands on disk named after its own package id.

## How it works

Google Play normally requires a signed-in account to issue a download. [Aurora Store](https://gitlab.com/AuroraOSS/AuroraStore) — an open-source Play Store client — ships with a pool of anonymous Google accounts and a "dispenser" service that hands out short-lived OAuth tokens for them on request, so the app can install things without ever asking you to sign in.

`nullapk` reverse-engineered that dispenser request (a device profile JSON POSTed to Aurora's own endpoint), uses it to obtain a token + matching anonymous account, and then hands that off to [`apkeep`](https://github.com/EFForg/apkeep) to perform the actual Google Play download. Each run requests a fresh token, so there's nothing to configure or keep alive.

## Installation

Requires Python 3.10+, [`pipx`](https://pipx.pypa.io/), and [`apkeep`](https://github.com/EFForg/apkeep) on `PATH`.

```sh
pipx install .
```

run from inside this directory. This installs the `nullapk` command.

## Usage

**Interactive (TUI):**

```sh
nullapk
```

Paste a Play Store URL (`https://play.google.com/store/apps/details?id=...`) or a package id, press Enter or click **Download**. A toast notification confirms success or failure, alongside a scrolling log of each step.

**Headless / scripting:**

```sh
nullapk com.example.app
nullapk "https://play.google.com/store/apps/details?id=com.example.app&pli=1"
nullapk com.example.app -o ~/some/other/dir
```

Files always save as `<output-dir>/<package-id>.apk`. Default `output-dir` is `apk/` inside this project folder.

## Project layout

```
nullapk/
├── playstore.py    # parses a Play Store URL / market:// URI / bare package id
├── dispenser.py     # talks to Aurora Store's anonymous auth dispenser
├── downloader.py     # wraps apkeep to perform the actual download
├── pipeline.py        # orchestrates parse -> token -> download, shared by both UIs
├── tui.py + tui.tcss   # interactive Textual front end
├── cli.py               # argument parsing / entry point
└── profiles/pixel3a.json # spoofed device profile sent to the dispenser
```

## Disclaimer

This wraps the same public mechanism Aurora Store (GPLv3) already uses for anonymous installs — it doesn't bypass any additional protection. Use it for things you're entitled to download (free apps, your own purchases, or APKs you have explicit authorization to pull for security research). You are responsible for complying with Google Play's Terms of Service in your jurisdiction.
