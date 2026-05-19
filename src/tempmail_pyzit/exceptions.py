from __future__ import annotations


class PyzitError(Exception):
    """Base class for all Pyzit SDK errors.
    Catch this to handle any SDK error in one place.
    """


class AuthenticationError(PyzitError):
    """Raised on HTTP 401 — invalid or missing API token."""


class PlanRequiredError(PyzitError):
    """Raised on HTTP 402/403 — endpoint needs a higher plan.

    Attributes:
        required_plan: The plan tier needed (e.g. "pro", "business").
    """

    def __init__(self, required_plan: str = "pro") -> None:
        self.required_plan = required_plan
        super().__init__(
            f"This endpoint requires the '{required_plan}' plan or higher."
        )


class ScopeError(PyzitError):
    """Raised on HTTP 403 — token doesn't have the required scope.

    Attributes:
        required_scope: The scope string needed (e.g. 'detailed:tempemail_check').
    """

    def __init__(self, required_scope: str = "") -> None:
        self.required_scope = required_scope
        super().__init__(
            f"Token missing required scope: '{required_scope}'. "
            f"Enable this scope in your Pyzit dashboard."
        )


class RateLimitError(PyzitError):
    """Raised on HTTP 429 — you've exceeded the request quota.

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header).
    """

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds.")


class APIError(PyzitError):
    """Raised for any unexpected non-2xx response.

    Attributes:
        status_code: HTTP status code returned by the API.
        response_body: Raw response text for debugging.
    """

    def __init__(self, status_code: int, response_body: str = "") -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"API returned HTTP {status_code}: {response_body[:200]}")


class TimeoutError(PyzitError):
    """Raised when the API request times out."""
