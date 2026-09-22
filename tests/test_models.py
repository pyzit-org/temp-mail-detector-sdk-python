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
        assert r.domain == "guerrillamail.com"
        assert r.risk_level == "low"
        assert r.reputation_score == 100
        assert r.is_trusted is True
        assert r.classification == "trusted"

    def test_should_reject_property(self):
        r = DetailedResult(**DETAILED_PAYLOAD)
        # Trusted email should not be rejected
        assert r.should_reject is False

    def test_dns_intelligence_parsed(self):
        r = DetailedResult(**DETAILED_PAYLOAD)
        assert r.details.has_mx is True
        assert r.details.mx_records == ["custom-whitelist.internal"]
        assert r.details.has_spf is True
        assert r.details.has_dmarc is True

    def test_should_flag_property(self):
        # Test with unknown classification
        payload = {**DETAILED_PAYLOAD, "classification": "unknown"}
        r = DetailedResult(**payload)
        assert r.should_flag is True

    def test_has_mx_property(self):
        r = DetailedResult(**DETAILED_PAYLOAD)
        assert r.has_mx is True

    def test_should_reject_when_disposable(self):
        payload = {**DETAILED_PAYLOAD, "is_disposable": True, "is_trusted": False}
        r = DetailedResult(**payload)
        assert r.should_reject is True

    def test_should_reject_when_untrusted(self):
        payload = {**DETAILED_PAYLOAD, "is_trusted": False}
        r = DetailedResult(**payload)
        assert r.should_reject is True


# ── BulkResult ───────────────────────────────────────────────────


class TestBulkResult:
    def test_parses_bulk_payload(self):
        r = BulkResult(**BULK_PAYLOAD)
        assert r.total == 2
        assert r.status == "mixed"
        assert r.disposable_count == 1
        assert len(r.results) == 2
        assert r.results[0].email == "hi@pyzit.com"
        assert r.results[0].is_disposable is False
        assert r.results[1].email == "x@mailnator.com"
        assert r.results[1].is_disposable is True

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

    def test_flagged_domains(self):
        r = BulkResult(**BULK_PAYLOAD)
        assert r.flagged_domains == ["mailnator.com"]

    def test_empty_bulk_result(self):
        r = BulkResult(
            total=0,
            status="clean",
            disposable_count=0,
            flagged_domains=[],
            results=[],
        )
        assert r.disposable_emails() == []
        assert r.clean_emails() == []
