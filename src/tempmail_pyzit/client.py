from __future__ import annotations

import random
import time
from typing import Any

import httpx

from ._http import BASE_URL, DEFAULT_TIMEOUT, build_headers, raise_for_status
from .exceptions import (
    APIError,
    PyzitError,
    TimeoutError,
)
from .models import BulkResult, CheckResult, DetailedResult


class TempMailClient:
    """Synchronous client for the Pyzit disposable email API.

    Usage::

        from tempmail_pyzit import TempMailClient

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
        max_retries: int = 2,
        fail_open: bool = False,
    ) -> None:
        self._headers = build_headers(api_token)
        self._timeout = timeout
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._fail_open = fail_open

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        attempts = 0
        while attempts <= self._max_retries:
            try:
                with httpx.Client(timeout=self._timeout) as http:
                    r = http.post(
                        self._base_url + path,
                        json=payload,
                        headers=self._headers,
                    )
                if r.status_code == 200:
                    return r.json()  # type: ignore[no-any-return]

                # Handle 429 rate limit with retry
                if r.status_code == 429 and attempts < self._max_retries:
                    retry_after = float(r.headers.get("Retry-After", 1))
                    time.sleep(retry_after + random.uniform(0.1, 0.4))
                    attempts += 1
                    continue

                # Handle 5xx errors with retry
                if r.status_code >= 500 and attempts < self._max_retries:
                    time.sleep((2**attempts) + random.uniform(0.1, 0.4))
                    attempts += 1
                    continue

                # Process non-retryable errors
                return raise_for_status(r)

            except httpx.TimeoutException as exc:
                if attempts < self._max_retries:
                    attempts += 1
                    time.sleep((2**attempts) + random.uniform(0.1, 0.4))
                    continue
                if self._fail_open:
                    return {
                        "email": payload.get("email", ""),
                        "is_disposable": False,
                        "status": "clean",
                    }
                raise TimeoutError("Request timed out.") from exc

            except (httpx.NetworkError, APIError) as exc:
                if attempts < self._max_retries:
                    attempts += 1
                    time.sleep((2**attempts) + random.uniform(0.1, 0.4))
                    continue
                if self._fail_open:
                    return {
                        "email": payload.get("email", ""),
                        "is_disposable": False,
                        "status": "clean",
                    }
                if isinstance(exc, APIError):
                    raise
                raise PyzitError(f"Network error: {exc}") from exc

        raise PyzitError("Max retries exceeded.")

    # ── public methods ──────────────────────────────────────────

    def check(self, email: str) -> CheckResult:
        """Check if an email is disposable.

        Args:
            email: The email address to validate.

        Returns:
            CheckResult with is_disposable and status fields.

        Raises:
            AuthenticationError: Bad token.
            InsufficientScopeError: Token lacks tmd:basic scope.
            QuotaExceededError: Monthly quota exhausted.
            RateLimitError: Too many requests.
            APIError: Unexpected server error.
        """
        data = self._post("/v1/tmd/check/", {"email": email})
        return CheckResult(**data)

    def detailed(self, email: str) -> DetailedResult:
        """Full analysis with DNS, reputation, and classification.

        Args:
            email: The email address to analyse.

        Returns:
            DetailedResult with classification, reputation_score, DNS details etc.

        Raises:
            AuthenticationError: Bad token.
            InsufficientScopeError: Token lacks tmd:detailed scope.
            QuotaExceededError: Monthly detailed quota exhausted.
            RateLimitError: Too many requests.
            APIError: Unexpected server error.
        """
        data = self._post("/v1/tmd/detailed/", {"email": email})
        return DetailedResult(**data)

    def bulk(self, emails: list[str]) -> BulkResult:
        """Validate many emails in a single request.

        Args:
            emails: List of email addresses (max depends on your plan:
                   Free=10, Pro=50, Scale=100).

        Returns:
            BulkResult with total, status, disposable_count,
            flagged_domains, and results array.

        Raises:
            AuthenticationError: Bad token.
            InsufficientScopeError: Token lacks tmd:basic scope.
            QuotaExceededError: Monthly quota exhausted.
            BatchLimitExceededError: Request exceeds your plan's batch size limit.
            RateLimitError: Too many requests.
            APIError: Unexpected server error.
        """
        data = self._post("/v1/tmd/bulk/", {"emails": emails})
        return BulkResult(**data)
