from __future__ import annotations

from typing import Any

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    PlanRequiredError,
    RateLimitError,
    ScopeError,
)

BASE_URL = "https://api-tempmail.pyzit.com/v1"
DEFAULT_TIMEOUT = 10.0


def build_headers(api_token: str) -> dict[str, str]:
    """Build the auth headers required by every request."""
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def raise_for_status(response: httpx.Response) -> dict[str, Any]:
    """Parse a response or raise the correct SDK exception."""

    if response.status_code == 200:
        result: dict[str, Any] = response.json()
        return result

    if response.status_code == 401:
        raise AuthenticationError("Invalid or missing API token.")

    if response.status_code == 403:
        try:
            body = response.json()
            detail = str(body.get("detail", ""))

            # scope error — "Token missing required scope: xyz"
            if "missing required scope" in detail.lower() or "scope" in detail.lower():
                # extract scope name from message if present
                scope = ""
                if ":" in detail:
                    # "Token missing required scope: detailed:tempemail_check"
                    scope = detail.split("scope:")[-1].strip()
                raise ScopeError(scope)

            # plan error — body contains required_plan key
            if "required_plan" in body or "upgrade" in str(body).lower():
                plan = body.get("required_plan", "pro")
                raise PlanRequiredError(plan)

        except (ValueError, KeyError):
            pass

        # fallback — bad/inactive token
        raise AuthenticationError(
            "Access denied (403). Check your API token is valid and active."
        )

    if response.status_code == 402:
        try:
            plan = response.json().get("required_plan", "pro")
        except ValueError:
            plan = "pro"
        raise PlanRequiredError(plan)

    if response.status_code == 429:
        retry = int(response.headers.get("Retry-After", 60))
        raise RateLimitError(retry)

    raise APIError(response.status_code, response.text)
