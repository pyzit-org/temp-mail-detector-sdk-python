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
    APIError,
    AuthenticationError,
    BatchLimitExceededError,
    BulkResult,
    CheckResult,
    DetailedResult,
    InsufficientScopeError,
    QuotaExceededError,
    RateLimitError,
    TimeoutError,
)

# ── check() happy paths ─────────────────────────────────────────


class TestCheck:
    @respx.mock
    def test_returns_check_result(self, client):
        respx.post(CHECK_URL).mock(
            return_value=httpx.Response(200, json=CLEAN_CHECK_PAYLOAD)
        )
        r = client.check("hi@pyzit.com")
        assert isinstance(r, CheckResult)

    @respx.mock
    def test_clean_email(self, client):
        respx.post(CHECK_URL).mock(
            return_value=httpx.Response(200, json=CLEAN_CHECK_PAYLOAD)
        )
        r = client.check("hi@pyzit.com")
        assert r.is_disposable is False
        assert r.is_clean is True
        assert r.status == "clean"

    @respx.mock
    def test_disposable_email(self, client):
        respx.post(CHECK_URL).mock(
            return_value=httpx.Response(200, json=DISPOSABLE_CHECK_PAYLOAD)
        )
        r = client.check("user@mailnator.com")
        assert r.is_disposable is True
        assert r.is_clean is False

    @respx.mock
    def test_sends_correct_json_body(self, client):
        route = respx.post(CHECK_URL).mock(
            return_value=httpx.Response(200, json=CLEAN_CHECK_PAYLOAD)
        )
        client.check("hi@pyzit.com")
        sent = route.calls.last.request
        import json

        body = json.loads(sent.content)
        assert body == {"email": "hi@pyzit.com"}

    @respx.mock
    def test_sends_auth_header(self, client):
        route = respx.post(CHECK_URL).mock(
            return_value=httpx.Response(200, json=CLEAN_CHECK_PAYLOAD)
        )
        client.check("hi@pyzit.com")
        headers = route.calls.last.request.headers
        assert headers["Authorization"] == "Bearer test-token-xyz"


# ── check() error handling ──────────────────────────────────────


class TestCheckErrors:
    @respx.mock
    def test_401_raises_authentication_error(self, client):
        respx.post(CHECK_URL).mock(return_value=httpx.Response(401))
        with pytest.raises(AuthenticationError):
            client.check("x@y.com")

    @respx.mock
    def test_429_raises_rate_limit_with_retry_after(self, client):
        respx.post(CHECK_URL).mock(
            return_value=httpx.Response(429, headers={"Retry-After": "45"})
        )
        with pytest.raises(RateLimitError) as exc:
            client.check("x@y.com")
        assert exc.value.retry_after == 45

    @respx.mock
    def test_500_raises_api_error(self, client):
        respx.post(CHECK_URL).mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(APIError) as exc:
            client.check("x@y.com")
        assert exc.value.status_code == 500

    @respx.mock
    def test_timeout_raises_timeout_error(self, client):
        respx.post(CHECK_URL).mock(side_effect=httpx.TimeoutException("timed out"))
        with pytest.raises(TimeoutError):
            client.check("x@y.com")


# ── detailed() ──────────────────────────────────────────────────


class TestDetailed:
    @respx.mock
    def test_returns_detailed_result(self, client):
        respx.post(DETAILED_URL).mock(
            return_value=httpx.Response(200, json=DETAILED_PAYLOAD)
        )
        r = client.detailed("user@guerrillamail.com")
        assert isinstance(r, DetailedResult)
        assert r.risk_level == "low"
        assert r.is_trusted is True
        assert r.classification == "trusted"
        assert r.should_reject is False

    @respx.mock
    def test_402_raises_quota_exceeded(self, client):
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
            client.detailed("x@y.com")
        assert exc.value.quota_type == "detailed"

    @respx.mock
    def test_403_raises_insufficient_scope(self, client):
        respx.post(DETAILED_URL).mock(
            return_value=httpx.Response(
                403,
                json={"detail": "API key lacks required scope: 'tmd:detailed'."},
            )
        )
        with pytest.raises(InsufficientScopeError) as exc:
            client.detailed("x@y.com")
        assert exc.value.required_scope == "tmd:detailed"


# ── bulk() ──────────────────────────────────────────────────────


class TestBulk:
    @respx.mock
    def test_returns_bulk_result(self, client):
        respx.post(BULK_URL).mock(return_value=httpx.Response(200, json=BULK_PAYLOAD))
        r = client.bulk(["hi@pyzit.com", "x@mailnator.com"])
        assert isinstance(r, BulkResult)
        assert r.total == 2
        assert r.status == "mixed"
        assert r.disposable_count == 1

    @respx.mock
    def test_sends_emails_list_in_body(self, client):
        route = respx.post(BULK_URL).mock(
            return_value=httpx.Response(200, json=BULK_PAYLOAD)
        )
        client.bulk(["hi@pyzit.com", "x@mailnator.com"])
        import json

        body = json.loads(route.calls.last.request.content)
        assert body["emails"] == ["hi@pyzit.com", "x@mailnator.com"]

    @respx.mock
    def test_bulk_result_helper_methods(self, client):
        respx.post(BULK_URL).mock(return_value=httpx.Response(200, json=BULK_PAYLOAD))
        r = client.bulk(["hi@pyzit.com", "x@mailnator.com"])
        assert r.clean_emails() == ["hi@pyzit.com"]
        assert r.disposable_emails() == ["x@mailnator.com"]
        assert r.flagged_domains == ["mailnator.com"]

    @respx.mock
    def test_402_raises_quota_exceeded_simple(self, client):
        respx.post(BULK_URL).mock(
            return_value=httpx.Response(
                402,
                json={
                    "detail": "You have exceeded your monthly simple check "
                    "quota. Please upgrade your plan.",
                    "code": "quota_exceeded",
                },
            )
        )
        with pytest.raises(QuotaExceededError) as exc:
            client.bulk(["a@b.com"])
        assert exc.value.quota_type == "simple"

    @respx.mock
    def test_400_raises_batch_limit_exceeded(self, client):
        respx.post(BULK_URL).mock(
            return_value=httpx.Response(
                400,
                json={
                    "detail": "Your plan allows a maximum of 10 emails per "
                    "bulk request. Upgrade your plan for higher limits."
                },
            )
        )
        with pytest.raises(BatchLimitExceededError) as exc:
            client.bulk(["a@b.com"] * 15)
        assert exc.value.max_allowed == 10


# ── base_url override (for integration / mock servers) ──────────


class TestClientConfig:
    @respx.mock
    def test_base_url_override(self):
        from tempmail_pyzit import TempMailClient

        custom = TempMailClient("tok", base_url="https://mock.local")
        respx.post("https://mock.local/v1/tmd/check/").mock(
            return_value=httpx.Response(200, json=CLEAN_CHECK_PAYLOAD)
        )
        r = custom.check("hi@pyzit.com")
        assert r.is_disposable is False
