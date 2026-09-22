from __future__ import annotations

import pytest

from tempmail_pyzit import (
    APIError,
    AuthenticationError,
    BatchLimitExceededError,
    InsufficientScopeError,
    PyzitError,
    QuotaExceededError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)


def test_all_errors_inherit_pyzit_error():
    for cls in [
        AuthenticationError,
        InsufficientScopeError,
        QuotaExceededError,
        BatchLimitExceededError,
        ValidationError,
        RateLimitError,
        APIError,
        TimeoutError,
    ]:
        assert issubclass(cls, PyzitError)


def test_rate_limit_default_retry_after():
    err = RateLimitError()
    assert err.retry_after == 1.0


def test_rate_limit_custom_retry_after():
    err = RateLimitError("Rate limit exceeded", retry_after=30)
    assert err.retry_after == 30
    assert "30" in str(err)


def test_quota_exceeded_stores_quota_type():
    err = QuotaExceededError("Monthly quota exceeded", quota_type="detailed")
    assert err.quota_type == "detailed"
    assert err.status_code == 402


def test_quota_exceeded_default_quota_type():
    err = QuotaExceededError("Monthly quota exceeded")
    assert err.quota_type == "simple"


def test_insufficient_scope_stores_scope():
    err = InsufficientScopeError(
        "API key lacks required scope", required_scope="tmd:detailed"
    )
    assert err.required_scope == "tmd:detailed"
    assert err.status_code == 403


def test_batch_limit_exceeded_stores_limits():
    err = BatchLimitExceededError("Batch too large", max_allowed=10, attempted=15)
    assert err.max_allowed == 10
    assert err.attempted == 15
    assert err.status_code == 400


def test_validation_error_stores_field_errors():
    field_errors = {"email": ["Invalid email format"]}
    err = ValidationError("Validation failed", field_errors=field_errors)
    assert err.field_errors == field_errors
    assert err.status_code == 400


def test_api_error_stores_status_and_body():
    err = APIError(
        "Internal Server Error",
        status_code=500,
        response_body="Internal Server Error",
    )
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
    with pytest.raises(PyzitError):
        raise QuotaExceededError("Quota exceeded")
    with pytest.raises(PyzitError):
        raise InsufficientScopeError("Missing scope", "tmd:basic")
    with pytest.raises(PyzitError):
        raise BatchLimitExceededError("Batch too large")
    with pytest.raises(PyzitError):
        raise ValidationError("Invalid input")
