"""
██████╗ ██╗   ██╗███████╗██╗████████╗
██╔══██╗╚██╗ ██╔╝╚══███╔╝██║╚══██╔══╝
██████╔╝ ╚████╔╝   ███╔╝ ██║   ██║
██╔═══╝   ╚██╔╝   ███╔╝  ██║   ██║
██║        ██║   ███████╗██║   ██║
╚═╝        ╚═╝   ╚══════╝╚═╝   ╚═╝

╔══════════════════════════════════════╗
║        PYZIT TEMPMAIL SDK            ║
║   Disposable Email Detection API     ║
╚══════════════════════════════════════╝

Official Python SDK for the Pyzit Disposable Email API.

Quick start::

    from tempmail_pyzit import TempMailClient

    client = TempMailClient("YOUR_TOKEN")

    result = client.check("user@example.com")

    print(result.is_disposable)  # True / False
"""

from .async_client import AsyncTempMailClient
from .client import TempMailClient
from .exceptions import (
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
from .models import (
    BulkItemResult,
    BulkResult,
    CheckResult,
    DetailedResult,
)

__version__ = "1.0.0"

__all__ = [
    # clients
    "TempMailClient",
    "AsyncTempMailClient",
    # models
    "CheckResult",
    "DetailedResult",
    "BulkResult",
    "BulkItemResult",
    # exceptions
    "PyzitError",
    "AuthenticationError",
    "InsufficientScopeError",
    "QuotaExceededError",
    "BatchLimitExceededError",
    "ValidationError",
    "RateLimitError",
    "APIError",
    "TimeoutError",
]
