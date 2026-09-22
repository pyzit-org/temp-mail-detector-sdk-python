from __future__ import annotations


class PyzitError(Exception):
    """Base class for all Pyzit SDK errors.
    Catch this to handle any SDK error in one place.
    """


class AuthenticationError(PyzitError):
    """Raised on HTTP 401 — invalid or missing API token.

    Attributes:
        status_code: 401
    """

    def __init__(self, message: str = "Invalid or inactive API key.") -> None:
        super().__init__(message)
        self.status_code = 401


class InsufficientScopeError(PyzitError):
    """Raised on HTTP 403 — token lacks required scope.

    Attributes:
        status_code: 403
        required_scope: The scope string needed (e.g. 'tmd:basic', 'tmd:detailed').
    """

    def __init__(self, message: str, required_scope: str = "") -> None:
        super().__init__(message)
        self.status_code = 403
        self.required_scope = required_scope


class QuotaExceededError(PyzitError):
    """Raised on HTTP 402 — monthly simple or detailed quota exhausted.

    Attributes:
        status_code: 402
        quota_type: Either "simple" or "detailed"
    """

    def __init__(self, message: str, quota_type: str = "simple") -> None:
        super().__init__(message)
        self.status_code = 402
        self.quota_type = quota_type


class BatchLimitExceededError(PyzitError):
    """Raised on HTTP 400 — bulk emails list exceeds plan batch limit.

    Attributes:
        status_code: 400
        max_allowed: Maximum batch size allowed by user's plan
        attempted: Number of emails attempted in the request
    """

    def __init__(self, message: str, max_allowed: int = 10, attempted: int = 0) -> None:
        super().__init__(message)
        self.status_code = 400
        self.max_allowed = max_allowed
        self.attempted = attempted


class ValidationError(PyzitError):
    """Raised on HTTP 400 — malformed email or request payload.

    Attributes:
        status_code: 400
        field_errors: Dictionary of field names to error messages
    """

    def __init__(
        self, message: str, field_errors: dict[str, str] | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = 400
        self.field_errors = field_errors or {}


class RateLimitError(PyzitError):
    """Raised on HTTP 429 — you've exceeded the request quota.

    Attributes:
        status_code: 429
        retry_after: Seconds to wait before retrying (from Retry-After header).
    """

    def __init__(
        self, message: str = "Rate limit exceeded.", retry_after: float = 1.0
    ) -> None:
        self.retry_after = retry_after
        self.status_code = 429
        super().__init__(f"{message} Retry after {retry_after} seconds.")


class APIError(PyzitError):
    """Raised for any unexpected non-2xx response.

    Attributes:
        status_code: HTTP status code returned by the API.
        response_body: Raw response text for debugging.
    """

    def __init__(
        self,
        message: str = "",
        status_code: int = 500,
        response_body: str = "",
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        if message:
            super().__init__(f"{message} (HTTP {status_code})")
        else:
            super().__init__(f"API returned HTTP {status_code}: {response_body[:200]}")


class TimeoutError(PyzitError):
    """Raised when the API request times out."""
