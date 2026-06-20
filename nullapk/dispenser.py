"""Client for Aurora Store's anonymous auth dispenser.

Aurora Store ships with a built-in pool of anonymous Google accounts and hands out
short-lived OAuth access tokens for them on request. This mirrors the request the
official Aurora Store app makes (reverse engineered from its `jl2`/`k10` classes),
trading a fake device profile for a token + an anonymous account email.
"""

import json
from dataclasses import dataclass
from importlib import resources

import requests

from nullapk.errors import DispenserError

DEFAULT_DISPENSER_URL = "https://auroraoss.com/api/auth"
DISPENSER_USER_AGENT = "com.aurora.store-4.8.3-75"
DEFAULT_DEVICE_PROFILE = "pixel3a.json"
REQUEST_TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class AuthToken:
    email: str
    auth_token: str
    gsf_id: str


def load_device_profile(name: str = DEFAULT_DEVICE_PROFILE) -> dict:
    data = resources.files("nullapk.profiles").joinpath(name).read_text()
    return json.loads(data)


def fetch_token(
    device_profile: dict | None = None,
    dispenser_url: str = DEFAULT_DISPENSER_URL,
) -> AuthToken:
    profile = device_profile if device_profile is not None else load_device_profile()

    try:
        response = requests.post(
            dispenser_url,
            json=profile,
            headers={
                "User-Agent": DISPENSER_USER_AGENT,
                "Content-Type": "application/json",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise DispenserError(f"Could not reach dispenser at {dispenser_url}: {exc}") from exc

    if response.status_code != 200:
        raise DispenserError(
            f"Dispenser returned HTTP {response.status_code}: {response.text[:300]}"
        )

    try:
        payload = response.json()
        auth_token = payload["authToken"]
        email = payload["email"]
        gsf_id = payload["gsfId"]
    except (ValueError, KeyError) as exc:
        raise DispenserError(f"Unexpected dispenser response shape: {exc}") from exc

    if not auth_token:
        raise DispenserError("Dispenser returned an empty auth token.")

    return AuthToken(email=email, auth_token=auth_token, gsf_id=gsf_id)
