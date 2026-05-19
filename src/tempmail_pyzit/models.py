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


# ── /v1/validate/detailed/ ───────────────────────────────────


class ReputationDetail(BaseModel):
    reputation_score: float
    is_disposable: bool
    disposable_confidence: float
    risk_level: str  # "low" | "medium" | "high"
    recommendation: str  # "accept" | "review" | "reject"


class Signals(BaseModel):
    positive: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)
    neutral: list[str] = Field(default_factory=list)


class MxRecord(BaseModel):
    """A single MX record with priority, exchange host, and resolved IPs."""

    priority: int
    exchange: str
    ips: list[str] = Field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.exchange} (priority={self.priority})"


class DnsIntelligence(BaseModel):
    has_mx: bool
    mx_records: list[MxRecord] = Field(default_factory=list)  # ← was list[str]
    has_a_record: bool
    has_spf: bool
    has_dmarc: bool
    error: str | None = None

    def mx_hostnames(self) -> list[str]:
        """Return just the exchange hostnames, e.g. ['mail.example.com']"""
        return [r.exchange for r in self.mx_records]

    def mx_ips(self) -> list[str]:
        """Return all resolved IPs across all MX records."""
        return [ip for r in self.mx_records for ip in r.ips]


class StabilityInfo(BaseModel):
    stability_score: float
    domain_age_days: int
    is_new_domain: bool
    risk_factors: list[str] = Field(default_factory=list)


class DetailedDetails(BaseModel):
    reputation: ReputationDetail
    signals: Signals
    dns_intelligence: DnsIntelligence
    stability: StabilityInfo


class DetailedResult(BaseModel):
    """Response from the Pro-tier /detailed/ endpoint."""

    email: str
    domain: str
    is_disposable: bool
    status: str
    reputation_score: float
    risk_level: str
    recommendation: str
    details: DetailedDetails

    @property
    def should_reject(self) -> bool:
        """True when the API recommends rejecting this email."""
        return self.recommendation == "reject"


# ── /v1/validate/bulk/ ───────────────────────────────────────


class BulkResult(BaseModel):
    """Response from the Business-tier /bulk/ endpoint."""

    results: dict[str, bool]  # {email: is_disposable}
    processed: int

    def disposable_emails(self) -> list[str]:
        """Return only the emails that ARE disposable."""
        return [e for e, disp in self.results.items() if disp]

    def clean_emails(self) -> list[str]:
        """Return only the emails that are NOT disposable."""
        return [e for e, disp in self.results.items() if not disp]
