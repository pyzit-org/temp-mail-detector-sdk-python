from __future__ import annotations

import re
from typing import Any

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    BatchLimitExceededError,
    InsufficientScopeError,
    QuotaExceededError,
    RateLimitError,
    ValidationError,
)

BASE_URL = "https://api.pyzit.com"
DEFAULT_TIMEOUT = 5.0


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

    try:
        body = response.json()
    except Exception:
        body = {"detail": response.text}

    detail = str(body.get("detail", ""))
    code = body.get("code", "")

    # 401 Unauthorized
    if response.status_code == 401:
        raise AuthenticationError(detail or "Invalid or inactive API key.")

    # 402 Payment Required (Quota Exceeded)
    if (
        response.status_code == 402
        or code == "quota_exceeded"
        or "quota" in detail.lower()
    ):
        quota_type = "detailed" if "detailed" in detail.lower() else "simple"
        raise QuotaExceededError(
            detail or "Monthly quota exceeded.", quota_type=quota_type
        )

    # 403 Forbidden (Scope Missing)
    if response.status_code == 403:
        required_scope = "tmd:detailed" if "tmd:detailed" in detail else "tmd:basic"
        raise InsufficientScopeError(
            detail or "API key lacks required scope.",
            required_scope=required_scope,
        )

    # 400 Bad Request
    if response.status_code == 400:
        if "maximum of" in detail and "bulk request" in detail:
            # Extract numbers if present
            match = re.search(r"maximum of (\d+)", detail)
            max_allowed = int(match.group(1)) if match else 10
            raise BatchLimitExceededError(detail, max_allowed=max_allowed)
        raise ValidationError(detail or "Validation error.", field_errors=body)

    # 429 Too Many Requests
    if response.status_code == 429:
        retry_after = 1.0
        header_val = response.headers.get("Retry-After")
        if header_val:
            try:
                retry_after = float(header_val)
            except ValueError:
                pass
        raise RateLimitError(detail or "Request throttled.", retry_after=retry_after)

    # 5xx / Other
    raise APIError(
        detail or f"HTTP {response.status_code}",
        status_code=response.status_code,
        response_body=response.text,
    )
