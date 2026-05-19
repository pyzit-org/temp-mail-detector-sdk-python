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

    from pyzit_tempmail import TempMailClient

    client = TempMailClient("YOUR_TOKEN")

    result = client.check("user@example.com")

    print(result.is_disposable)  # True / False
"""

from .async_client import AsyncTempMailClient
from .client import TempMailClient
from .exceptions import (
    APIError,
    AuthenticationError,
    PlanRequiredError,
    PyzitError,
    RateLimitError,
    ScopeError,
    TimeoutError,
)
from .models import (
    BulkResult,
    CheckResult,
    DetailedResult,
    MxRecord,
)

__version__ = "0.1.0"

__all__ = [
    # clients
    "TempMailClient",
    "AsyncTempMailClient",
    # models
    "CheckResult",
    "DetailedResult",
    "BulkResult",
    "MxRecord",
    # exceptions
    "PyzitError",
    "AuthenticationError",
    "ScopeError",
    "PlanRequiredError",
    "RateLimitError",
    "APIError",
    "TimeoutError",
]
