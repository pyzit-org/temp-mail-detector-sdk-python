from __future__ import annotations

import httpx
import pytest
import respx
from fixtures import (
    BULK_PAYLOAD,
    BULK_URL,
    CHECK_URL,
    CLEAN_CHECK_PAYLOAD,
    DETAILED_PAYLOAD,
    DETAILED_URL,
    DISPOSABLE_CHECK_PAYLOAD,
)

from tempmail_pyzit import (
    AuthenticationError,
    BulkResult,
    CheckResult,
    DetailedResult,
    InsufficientScopeError,
    QuotaExceededError,
    RateLimitError,
    TimeoutError,
)

# pytest-asyncio with asyncio_mode="auto" in pyproject.toml
# means no @pytest.mark.asyncio needed — async def tests just work


class TestAsyncCheck:
    @respx.mock
    async def test_clean_email(self, async_client):
        respx.post(CHECK_URL).mock(
            return_value=httpx.Response(200, json=CLEAN_CHECK_PAYLOAD)
        )
        r = await async_client.check("hi@pyzit.com")
        assert isinstance(r, CheckResult)
        assert r.is_disposable is False

    @respx.mock
    async def test_disposable_email(self, async_client):
        respx.post(CHECK_URL).mock(
            return_value=httpx.Response(200, json=DISPOSABLE_CHECK_PAYLOAD)
        )
        r = await async_client.check("user@mailnator.com")
        assert r.is_disposable is True

    @respx.mock
    async def test_401_raises_authentication_error(self, async_client):
        respx.post(CHECK_URL).mock(return_value=httpx.Response(401))
        with pytest.raises(AuthenticationError):
            await async_client.check("x@y.com")

    @respx.mock
    async def test_429_carries_retry_after(self, async_client):
        respx.post(CHECK_URL).mock(
            return_value=httpx.Response(429, headers={"Retry-After": "20"})
        )
        with pytest.raises(RateLimitError) as exc:
            await async_client.check("x@y.com")
        assert exc.value.retry_after == 20

    @respx.mock
    async def test_timeout_raises_timeout_error(self, async_client):
        respx.post(CHECK_URL).mock(side_effect=httpx.TimeoutException("timed out"))
        with pytest.raises(TimeoutError):
            await async_client.check("x@y.com")


class TestAsyncDetailed:
    @respx.mock
    async def test_returns_detailed_result(self, async_client):
        respx.post(DETAILED_URL).mock(
            return_value=httpx.Response(200, json=DETAILED_PAYLOAD)
        )
        r = await async_client.detailed("user@guerrillamail.com")
        assert isinstance(r, DetailedResult)
        assert r.is_trusted is True
        assert r.classification == "trusted"
        assert r.should_reject is False

    @respx.mock
    async def test_402_raises_quota_exceeded(self, async_client):
        respx.post(DETAILED_URL).mock(
            return_value=httpx.Response(
                402,
                json={
                    "detail": "You have exceeded your monthly detailed check "
                    "quota. Please upgrade your plan.",
                    "code": "quota_exceeded",
                },
            )
        )
        with pytest.raises(QuotaExceededError) as exc:
            await async_client.detailed("x@y.com")
        assert exc.value.quota_type == "detailed"

    @respx.mock
    async def test_403_raises_insufficient_scope(self, async_client):
        respx.post(DETAILED_URL).mock(
            return_value=httpx.Response(
                403,
                json={"detail": "API key lacks required scope: 'tmd:detailed'."},
            )
        )
        with pytest.raises(InsufficientScopeError) as exc:
            await async_client.detailed("x@y.com")
        assert exc.value.required_scope == "tmd:detailed"


class TestAsyncBulk:
    @respx.mock
    async def test_returns_bulk_result(self, async_client):
        respx.post(BULK_URL).mock(return_value=httpx.Response(200, json=BULK_PAYLOAD))
        r = await async_client.bulk(["hi@pyzit.com", "x@mailnator.com"])
        assert isinstance(r, BulkResult)
        assert r.total == 2
        assert r.status == "mixed"
        assert r.disposable_emails() == ["x@mailnator.com"]
