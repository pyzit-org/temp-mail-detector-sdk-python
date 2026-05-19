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
    BulkResult,
    CheckResult,
    DetailedResult,
    PlanRequiredError,
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
        r = client.detailed("x@new-domain.io")
        assert isinstance(r, DetailedResult)
        assert r.risk_level == "high"
        assert r.should_reject is True

    @respx.mock
    def test_402_raises_plan_required(self, client):
        respx.post(DETAILED_URL).mock(
            return_value=httpx.Response(402, json={"required_plan": "pro"})
        )
        with pytest.raises(PlanRequiredError) as exc:
            client.detailed("x@y.com")
        assert exc.value.required_plan == "pro"

    @respx.mock
    def test_403_also_raises_plan_required(self, client):
        respx.post(DETAILED_URL).mock(
            return_value=httpx.Response(403, json={"required_plan": "pro"})
        )
        with pytest.raises(PlanRequiredError):
            client.detailed("x@y.com")


# ── bulk() ──────────────────────────────────────────────────────


class TestBulk:
    @respx.mock
    def test_returns_bulk_result(self, client):
        respx.post(BULK_URL).mock(return_value=httpx.Response(200, json=BULK_PAYLOAD))
        r = client.bulk(["hi@pyzit.com", "x@mailnator.com"])
        assert isinstance(r, BulkResult)
        assert r.processed == 2

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
    def test_402_raises_plan_required_business(self, client):
        respx.post(BULK_URL).mock(
            return_value=httpx.Response(402, json={"required_plan": "business"})
        )
        with pytest.raises(PlanRequiredError) as exc:
            client.bulk(["a@b.com"])
        assert exc.value.required_plan == "business"


# ── base_url override (for integration / mock servers) ──────────


class TestClientConfig:
    @respx.mock
    def test_base_url_override(self):
        from tempmail_pyzit import TempMailClient

        custom = TempMailClient("tok", base_url="https://mock.local/v1")
        respx.post("https://mock.local/v1/validate/check/").mock(
            return_value=httpx.Response(200, json=CLEAN_CHECK_PAYLOAD)
        )
        r = custom.check("hi@pyzit.com")
        assert r.is_disposable is False
