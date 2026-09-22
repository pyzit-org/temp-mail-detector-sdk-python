from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx

from ._http import BASE_URL, DEFAULT_TIMEOUT, build_headers, raise_for_status
from .exceptions import (
    APIError,
    PyzitError,
    TimeoutError,
)
from .models import BulkResult, CheckResult, DetailedResult


class AsyncTempMailClient:
    """Async client for the Pyzit disposable email API.

    Usage (FastAPI example)::

        from tempmail_pyzit import AsyncTempMailClient

        client = AsyncTempMailClient("YOUR_API_TOKEN")

        @app.post("/register")
        async def register(email: str):
            result = await client.check(email)
            if result.is_disposable:
                raise HTTPException(400, "Disposable emails not allowed")
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

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        attempts = 0
        while attempts <= self._max_retries:
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as http:
                    r = await http.post(
                        self._base_url + path,
                        json=payload,
                        headers=self._headers,
                    )
                if r.status_code == 200:
                    return r.json()  # type: ignore[no-any-return]

                # Handle 429 rate limit with retry
                if r.status_code == 429 and attempts < self._max_retries:
                    retry_after = float(r.headers.get("Retry-After", 1))
                    await asyncio.sleep(retry_after + random.uniform(0.1, 0.4))
                    attempts += 1
                    continue

                # Handle 5xx errors with retry
                if r.status_code >= 500 and attempts < self._max_retries:
                    await asyncio.sleep((2**attempts) + random.uniform(0.1, 0.4))
                    attempts += 1
                    continue

                # Process non-retryable errors
                return raise_for_status(r)

            except httpx.TimeoutException as exc:
                if attempts < self._max_retries:
                    attempts += 1
                    await asyncio.sleep((2**attempts) + random.uniform(0.1, 0.4))
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
                    await asyncio.sleep((2**attempts) + random.uniform(0.1, 0.4))
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

    async def check(self, email: str) -> CheckResult:
        data = await self._post("/v1/tmd/check/", {"email": email})
        return CheckResult(**data)

    async def detailed(self, email: str) -> DetailedResult:
        data = await self._post("/v1/tmd/detailed/", {"email": email})
        return DetailedResult(**data)

    async def bulk(self, emails: list[str]) -> BulkResult:
        data = await self._post("/v1/tmd/bulk/", {"emails": emails})
        return BulkResult(**data)
