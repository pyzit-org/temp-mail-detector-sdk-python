from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ── /v1/tmd/check/ ───────────────────────────────────────────


class CheckResult(BaseModel):
    """Response from the /v1/tmd/check/ endpoint."""

    email: str
    is_disposable: bool
    is_privacy_relay: bool = False
    status: str  # "clean" | "disposable" | "privacy_relay"
    relay_provider: str | None = None
    provider_name: str | None = None
    rule_applied: str | None = None
    rule_details: dict[str, Any] | None = None

    @property
    def is_clean(self) -> bool:
        """Shorthand: True when the email is NOT disposable."""
        return not self.is_disposable


# ── /v1/tmd/detailed/ ────────────────────────────────────────


class DetailedDetails(BaseModel):
    """Detailed DNS and MX verification intelligence."""

    has_mx: bool
    mx_records: list[str] = Field(default_factory=list)
    has_a: bool = False
    a_records: list[str] = Field(default_factory=list)
    has_spf: bool = False
    spf_record: str | None = None
    has_dmarc: bool = False
    dmarc_record: str | None = None


class DetailedResult(BaseModel):
    """Response from the /v1/tmd/detailed/ endpoint."""

    email: str
    domain: str
    is_disposable: bool
    is_trusted: bool
    is_privacy_relay: bool = False
    relay_provider: str | None = None
    provider_name: str | None = None
    classification: (
        str  # "trusted" | "disposable" | "privacy_relay" | "suspicious" | "clean"
    )
    reputation_score: int  # 0-100 scale
    risk_level: str  # "low" | "medium" | "high"
    is_valid_format: bool = True
    cached: bool = False
    rule_applied: str | None = None
    rule_details: dict[str, Any] | None = None
    details: DetailedDetails
    status: str = "clean"  # "clean" | "disposable" | "privacy_relay"

    @property
    def is_clean(self) -> bool:
        """Shorthand: True when the email is NOT disposable."""
        return not self.is_disposable

    @property
    def should_reject(self) -> bool:
        """True when the email should be rejected (disposable or untrusted)."""
        return self.is_disposable or not self.is_trusted

    @property
    def should_flag(self) -> bool:
        """True when the email needs manual review."""
        return self.classification in ("unknown", "suspicious")

    @property
    def has_mx(self) -> bool:
        """Shorthand for DNS MX record check."""
        return self.details.has_mx


# ── /v1/tmd/bulk/ ────────────────────────────────────────────


class BulkItemResult(BaseModel):
    """Individual result for a single email in bulk check."""

    email: str
    is_disposable: bool
    is_privacy_relay: bool = False
    status: str  # "clean" | "disposable" | "privacy_relay"
    relay_provider: str | None = None
    provider_name: str | None = None
    rule_applied: str | None = None
    rule_details: dict[str, Any] | None = None

    @property
    def is_clean(self) -> bool:
        """Shorthand: True when the email is NOT disposable."""
        return not self.is_disposable


class BulkResult(BaseModel):
    """Response from the bulk endpoint."""

    total: int
    status: str  # "clean" | "disposable" | "privacy_relay" | "mixed"
    disposable_count: int
    privacy_relay_count: int = 0
    flagged_domains: list[str] = Field(default_factory=list)
    results: list[BulkItemResult] = Field(default_factory=list)

    def disposable_emails(self) -> list[str]:
        """Return only the emails that ARE disposable."""
        return [item.email for item in self.results if item.is_disposable]

    def clean_emails(self) -> list[str]:
        """Return only the emails that are NOT disposable."""
        return [item.email for item in self.results if not item.is_disposable]

    def privacy_relay_emails(self) -> list[str]:
        """Return only the emails that are privacy relays."""
        return [item.email for item in self.results if item.is_privacy_relay]
