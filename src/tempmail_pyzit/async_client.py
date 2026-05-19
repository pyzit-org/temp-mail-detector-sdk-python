from __future__ import annotations

from typing import Any

import httpx

from ._http import BASE_URL, DEFAULT_TIMEOUT, build_headers, raise_for_status
from .exceptions import TimeoutError
from .models import BulkResult, CheckResult, DetailedResult


class AsyncTempMailClient:
    """Async client for the Pyzit disposable email API.

    Usage (FastAPI example)::

        from pyzit_tempmail import AsyncTempMailClient

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
    ) -> None:
        self._headers = build_headers(api_token)
        self._timeout = timeout
        self._base_url = base_url.rstrip("/")

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as http:
                r = await http.post(
                    self._base_url + path,
                    json=payload,
                    headers=self._headers,
                )
            return raise_for_status(r)
        except httpx.TimeoutException as exc:
            raise TimeoutError("Request timed out.") from exc

    async def check(self, email: str) -> CheckResult:
        data = await self._post("/validate/check/", {"email": email})
        return CheckResult(**data)

    async def detailed(self, email: str) -> DetailedResult:
        data = await self._post("/validate/detailed/", {"email": email})
        return DetailedResult(**data)

    async def bulk(self, emails: list[str]) -> BulkResult:
        data = await self._post("/validate/bulk/", {"emails": emails})
        return BulkResult(**data)
