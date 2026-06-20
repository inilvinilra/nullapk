"""Parsing helpers for turning a Play Store link (or bare package id) into a package id."""

import re
from urllib.parse import parse_qs, urlparse

from nullapk.errors import InvalidTargetError

_PACKAGE_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$")


def is_valid_package_id(value: str) -> bool:
    return bool(_PACKAGE_ID_RE.match(value))


def extract_package_id(target: str) -> str:
    """Accept a Play Store URL, a market:// URI, or a raw package id and return the package id."""
    target = target.strip().strip("'\"")
    if not target:
        raise InvalidTargetError("Input is empty.")

    if is_valid_package_id(target):
        return target

    parsed = urlparse(target)
    if parsed.scheme in ("http", "https", "market") and parsed.query:
        query = parse_qs(parsed.query)
        candidates = query.get("id")
        if candidates and is_valid_package_id(candidates[0]):
            return candidates[0]

    if parsed.scheme == "market" and parsed.netloc == "details":
        query = parse_qs(parsed.query)
        candidates = query.get("id")
        if candidates and is_valid_package_id(candidates[0]):
            return candidates[0]

    raise InvalidTargetError(
        f"Could not extract a package id from {target!r}. "
        "Expected a Play Store URL (...?id=com.example.app) or a bare package id."
    )
