from __future__ import annotations

import pytest

from tempmail_pyzit import (
    APIError,
    AuthenticationError,
    PlanRequiredError,
    PyzitError,
    RateLimitError,
    TimeoutError,
)


def test_all_errors_inherit_pyzit_error():
    for cls in [
        AuthenticationError,
        PlanRequiredError,
        RateLimitError,
        APIError,
        TimeoutError,
    ]:
        assert issubclass(cls, PyzitError)


def test_rate_limit_default_retry_after():
    err = RateLimitError()
    assert err.retry_after == 60


def test_rate_limit_custom_retry_after():
    err = RateLimitError(retry_after=30)
    assert err.retry_after == 30
    assert "30" in str(err)


def test_plan_required_stores_plan():
    err = PlanRequiredError("business")
    assert err.required_plan == "business"
    assert "business" in str(err)


def test_plan_required_default_plan():
    err = PlanRequiredError()
    assert err.required_plan == "pro"


def test_api_error_stores_status_and_body():
    err = APIError(500, "Internal Server Error")
    assert err.status_code == 500
    assert "Internal Server Error" in err.response_body
    assert "500" in str(err)


def test_catching_base_catches_all():
    with pytest.raises(PyzitError):
        raise RateLimitError()
    with pytest.raises(PyzitError):
        raise AuthenticationError("bad")
    with pytest.raises(PyzitError):
        raise APIError(503, "down")
