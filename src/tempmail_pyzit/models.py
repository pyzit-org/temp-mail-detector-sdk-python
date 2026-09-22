from __future__ import annotations

from pydantic import BaseModel, Field

# ── /v1/validate/check/ ───────────────────────────────────────


class CheckResult(BaseModel):
    """Response from the free-tier /check/ endpoint."""

    email: str
    is_disposable: bool
    status: str  # "clean" | "disposable"

    @property
    def is_clean(self) -> bool:
        """Shorthand: True when the email is NOT disposable."""
        return not self.is_disposable


# ── /v1/tmd/detailed/ ───────────────────────────────────


class DetailedDetails(BaseModel):
    """Detailed DNS and classification information."""

    has_mx: bool
    mx_records: list[str] = Field(default_factory=list)
    has_a: bool
    a_records: list[str] = Field(default_factory=list)
    has_spf: bool
    spf_record: str | None = None
    has_dmarc: bool
    dmarc_record: str | None = None


class DetailedResult(BaseModel):
    """Response from the detailed endpoint."""

    email: str
    domain: str
    is_disposable: bool
    is_trusted: bool
    classification: str  # "trusted" | "disposable" | "unknown"
    reputation_score: int  # 0-100 scale
    risk_level: str  # "low" | "medium" | "high"
    is_valid_format: bool
    rule_applied: str | None = None
    details: DetailedDetails
    status: str  # "clean" | "disposable"

    @property
    def should_reject(self) -> bool:
        """True when the email should be rejected (disposable or untrusted)."""
        return self.is_disposable or not self.is_trusted

    @property
    def should_flag(self) -> bool:
        """True when the email needs manual review."""
        return self.classification == "unknown"

    @property
    def has_mx(self) -> bool:
        """Shorthand for DNS MX record check."""
        return self.details.has_mx


# ── /v1/tmd/bulk/ ───────────────────────────────────────


class BulkItemResult(BaseModel):
    """Individual result for a single email in bulk check."""

    email: str
    is_disposable: bool
    status: str  # "clean" | "disposable"


class BulkResult(BaseModel):
    """Response from the bulk endpoint."""

    total: int
    status: str  # "clean" | "disposable" | "mixed"
    disposable_count: int
    flagged_domains: list[str] = Field(default_factory=list)
    results: list[BulkItemResult] = Field(default_factory=list)

    def disposable_emails(self) -> list[str]:
        """Return only the emails that ARE disposable."""
        return [item.email for item in self.results if item.is_disposable]

    def clean_emails(self) -> list[str]:
        """Return only the emails that are NOT disposable."""
        return [item.email for item in self.results if not item.is_disposable]
