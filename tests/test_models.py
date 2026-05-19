from __future__ import annotations

import pytest
from fixtures import (
    BULK_PAYLOAD,
    CLEAN_CHECK_PAYLOAD,
    DETAILED_PAYLOAD,
    DISPOSABLE_CHECK_PAYLOAD,
)
from pydantic import ValidationError

from tempmail_pyzit.models import BulkResult, CheckResult, DetailedResult

# ── CheckResult ─────────────────────────────────────────────────


class TestCheckResult:
    def test_parses_clean_email(self):
        r = CheckResult(**CLEAN_CHECK_PAYLOAD)
        assert r.email == "hi@pyzit.com"
        assert r.is_disposable is False
        assert r.status == "clean"

    def test_is_clean_property_true_when_not_disposable(self):
        r = CheckResult(**CLEAN_CHECK_PAYLOAD)
        assert r.is_clean is True

    def test_is_clean_property_false_when_disposable(self):
        r = CheckResult(**DISPOSABLE_CHECK_PAYLOAD)
        assert r.is_clean is False
        assert r.is_disposable is True

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            CheckResult(email="x@y.com")  # missing is_disposable + status

    def test_extra_fields_ignored(self):
        # API may add new fields — we must not crash
        r = CheckResult(**CLEAN_CHECK_PAYLOAD, future_field="ignored")
        assert r.email == "hi@pyzit.com"


# ── DetailedResult ───────────────────────────────────────────────


class TestDetailedResult:
    def test_parses_full_payload(self):
        r = DetailedResult(**DETAILED_PAYLOAD)
        assert r.domain == "new-domain.io"
        assert r.risk_level == "high"
        assert r.reputation_score == 0.0

    def test_should_reject_property(self):
        r = DetailedResult(**DETAILED_PAYLOAD)
        assert r.should_reject is True

    def test_dns_intelligence_parsed(self):
        r = DetailedResult(**DETAILED_PAYLOAD)
        assert r.details.dns_intelligence.has_mx is False
        assert r.details.dns_intelligence.mx_records == []
        assert r.details.dns_intelligence.error is None

    def test_signals_parsed(self):
        r = DetailedResult(**DETAILED_PAYLOAD)
        assert "no_mx_records" in r.details.signals.negative
        assert r.details.signals.positive == []

    def test_stability_parsed(self):
        r = DetailedResult(**DETAILED_PAYLOAD)
        assert r.details.stability.is_new_domain is True
        assert r.details.stability.domain_age_days == 0

    def test_should_reject_false_when_accept(self):
        payload = {**DETAILED_PAYLOAD, "recommendation": "accept"}
        r = DetailedResult(**payload)
        assert r.should_reject is False


# ── BulkResult ───────────────────────────────────────────────────


class TestBulkResult:
    def test_parses_bulk_payload(self):
        r = BulkResult(**BULK_PAYLOAD)
        assert r.processed == 2
        assert r.results["hi@pyzit.com"] is False
        assert r.results["x@mailnator.com"] is True

    def test_disposable_emails_helper(self):
        r = BulkResult(**BULK_PAYLOAD)
        disp = r.disposable_emails()
        assert "x@mailnator.com" in disp
        assert "hi@pyzit.com" not in disp

    def test_clean_emails_helper(self):
        r = BulkResult(**BULK_PAYLOAD)
        clean = r.clean_emails()
        assert "hi@pyzit.com" in clean
        assert "x@mailnator.com" not in clean

    def test_empty_bulk_result(self):
        r = BulkResult(results={}, processed=0)
        assert r.disposable_emails() == []
        assert r.clean_emails() == []
