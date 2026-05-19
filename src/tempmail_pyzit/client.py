from __future__ import annotations

from typing import Any

import httpx

from ._http import BASE_URL, DEFAULT_TIMEOUT, build_headers, raise_for_status
from .exceptions import TimeoutError
from .models import BulkResult, CheckResult, DetailedResult


class TempMailClient:
    """Synchronous client for the Pyzit disposable email API.

    Usage::

        from pyzit_tempmail import TempMailClient

        client = TempMailClient("YOUR_API_TOKEN")
        result = client.check("user@example.com")
        if result.is_disposable:
            raise ValueError("Disposable emails not allowed")
    """

    def __init__(
        self,
        api_token: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        base_url: str = BASE_URL,
    ) -> None:
        self._headers = build_headers(api_token)
        self._timeout = timeout
        self._base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=self._timeout) as http:
                r = http.post(
                    self._base_url + path,
                    json=payload,
                    headers=self._headers,
                )
            return raise_for_status(r)
        except httpx.TimeoutException as exc:
            raise TimeoutError("Request timed out.") from exc

    # ── public methods ──────────────────────────────────────────

    def check(self, email: str) -> CheckResult:
        """Check if an email is disposable (free tier).

        Args:
            email: The email address to validate.

        Returns:
            CheckResult with is_disposable and status fields.

        Raises:
            AuthenticationError: Bad token.
            RateLimitError: Too many requests.
            APIError: Unexpected server error.
        """
        data = self._post("/validate/check/", {"email": email})
        return CheckResult(**data)

    def detailed(self, email: str) -> DetailedResult:
        """Full analysis with DNS, signals, reputation (Pro tier).

        Args:
            email: The email address to analyse.

        Returns:
            DetailedResult with risk_level, signals, dns_intelligence etc.

        Raises:
            PlanRequiredError: Your token doesn't have Pro access.
        """
        data = self._post("/validate/detailed/", {"email": email})
        return DetailedResult(**data)

    def bulk(self, emails: list[str]) -> BulkResult:
        """Validate many emails in a single request (Business tier).

        Args:
            emails: List of email addresses (max 100 per request).

        Returns:
            BulkResult with results dict and processed count.

        Raises:
            PlanRequiredError: Your token doesn't have Business access.
        """
        data = self._post("/validate/bulk/", {"emails": emails})
        return BulkResult(**data)
