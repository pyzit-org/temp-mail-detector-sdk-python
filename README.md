<div align="center">

```
██████╗ ██╗   ██╗███████╗██╗████████╗
██╔══██╗╚██╗ ██╔╝╚══███╔╝██║╚══██╔══╝
██████╔╝ ╚████╔╝   ███╔╝ ██║   ██║
██╔═══╝   ╚██╔╝   ███╔╝  ██║   ██║
██║        ██║   ███████╗██║   ██║
╚═╝        ╚═╝   ╚══════╝╚═╝   ╚═╝

████████╗███████╗███╗   ███╗██████╗ ███╗   ███╗ █████╗ ██╗██╗
╚══██╔══╝██╔════╝████╗ ████║██╔══██╗████╗ ████║██╔══██╗██║██║
   ██║   █████╗  ██╔████╔██║██████╔╝██╔████╔██║███████║██║██║
   ██║   ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██║╚██╔╝██║██╔══██║██║██║
   ██║   ███████╗██║ ╚═╝ ██║██║     ██║ ╚═╝ ██║██║  ██║██║███████╗
   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
```

**The official Python SDK for the [Pyzit Disposable Email Detector API](https://temp-mail-detector.pyzit.com)**

Stop fake signups. Block throwaway addresses. Protect your platform.

[![PyPI version](https://img.shields.io/pypi/v/tempmail-pyzit?color=1D9E75&labelColor=0f0f0f&style=flat-square)](https://pypi.org/project/tempmail-pyzit/)
[![Python](https://img.shields.io/pypi/pyversions/tempmail-pyzit?color=1D9E75&labelColor=0f0f0f&style=flat-square)](https://pypi.org/project/tempmail-pyzit/)
[![License](https://img.shields.io/pypi/l/tempmail-pyzit?color=1D9E75&labelColor=0f0f0f&style=flat-square)](LICENSE)
[![mypy](https://img.shields.io/badge/type--checked-mypy%20strict-1D9E75?labelColor=0f0f0f&style=flat-square)](https://mypy.readthedocs.io/)
[![uv](https://img.shields.io/badge/built%20with-uv-1D9E75?labelColor=0f0f0f&style=flat-square)](https://github.com/astral-sh/uv)

</div>

---

## ◈ What is this?

`tempmail-pyzit` is the official Python client for the **Pyzit Disposable Email API** — a service that detects throwaway, temporary, and fake email addresses in real time.

```
User submits email          SDK validates it              Your app decides
─────────────────           ─────────────────             ───────────────
user@mailnator.com  ──────► is_disposable: True  ──────►  ✗  Reject signup
hi@yourcompany.com  ──────► is_disposable: False ──────►  ✓  Allow signup
```

Works with **Django**, **Flask**, **FastAPI**, plain scripts — sync and async both supported out of the box.

---

## ◈ Table of contents

- [Installation](#-installation)
- [Quick start](#-quick-start)
- [API tiers](#-api-tiers)
- [All methods](#-all-methods)
  - [check()](#checkresult--checkemail-str)
  - [detailed()](#detailedresult--detailedemail-str)
  - [bulk()](#bulkresult--bulkemails-liststr)
- [Async usage](#-async-usage)
- [Response models](#-response-models)
- [Error handling](#-error-handling)
- [Framework integrations](#-framework-integrations)
- [Configuration](#-configuration)
- [Development](#-development)

---

## ◈ Installation

```bash
pip install tempmail-pyzit
```

Or with [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv add tempmail-pyzit
```

**Requirements:** Python 3.9 or higher.

---

## ◈ Quick start

```python
from tempmail_pyzit import TempMailClient

client = TempMailClient("YOUR_API_TOKEN")

result = client.check("user@example.com")

if result.is_disposable:
    print("❌ Disposable email — rejected")
else:
    print("✅ Looks clean — allowed")
```

Get your API token at [temp-mail-detector.pyzit.com](https://temp-mail-detector.pyzit.com).

> **Important:** API tokens now use the prefix `pyzit_live_...` (e.g., `pyzit_live_7b19e2f4a5c84d12903456789abcdef0`).

> **Tip:** Store your token in an environment variable, never hard-code it.
> ```python
> import os
> client = TempMailClient(os.environ["PYZIT_TOKEN"])
> ```

---

## ◈ API tiers & quota model

**New architecture:** Plans determine quota, not endpoint access. Every plan can use all endpoints.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         QUOTA MODEL                                  │
├──────────────────┬─────────────┬──────────────────────────────────┤
│  Plan            │  Simple     │  Detailed                        │
│                  │  Quota/mo   │  Quota/mo                        │
├──────────────────┼─────────────┼──────────────────────────────────┤
│  Free Developer  │  1,000      │  20                              │
│  Pro             │  50,000     │  1,000                           │
│  Scale           │  500,000    │  25,000                          │
│  Enterprise      │  Custom     │  Custom                          │
└──────────────────┴─────────────┴──────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      BULK BATCH LIMITS                                │
├──────────────────┬─────────────┬──────────────────────────────────┤
│  Plan            │  Max Emails │  Notes                           │
├──────────────────┼─────────────┼──────────────────────────────────┤
│  Free Developer  │  10         │  Per request                     │
│  Pro             │  50         │  Per request                     │
│  Scale           │  100        │  Per request                     │
│  Enterprise      │  500+       │  Custom configured               │
└──────────────────┴─────────────┴──────────────────────────────────┘
```

**Important:** 
- **Unlimited API keys** across all plans
- **Token scopes** determine access: `tmd:basic` (check + bulk), `tmd:detailed` (detailed), `tmd:*` (all)
- Any user on any plan can create tokens with any scope

---

## ◈ All methods

### `CheckResult` ← `check(email: str)`

The fastest check. One email in, one decision out. Uses `simple_quota`.

```python
result = client.check("user@mailnator.com")

result.email          # "user@mailnator.com"
result.is_disposable  # True
result.status         # "disposable"
result.is_clean       # False  (convenience property, opposite of is_disposable)
```

**Response shape:**

```
CheckResult
├── email           str    — the email you submitted
├── is_disposable   bool   — True = block it
├── status          str    — "clean" | "disposable"
└── is_clean        bool   — shorthand for not is_disposable
```

---

### `DetailedResult` ← `detailed(email: str)`

Full forensic analysis. DNS records (MX, A, SPF, DMARC), reputation scoring,
domain classification. Uses `detailed_quota`. Requires `tmd:detailed` scope.

```python
result = client.detailed("hi@pyzit.com")

result.risk_level       # "low"
result.classification   # "trusted"
result.reputation_score # 100  (int, 0 to 100)
result.should_reject    # False  (convenience property)

# DNS intelligence
result.has_mx           # True
result.details.has_mx   # True
result.details.mx_records  # ["mail1.pyzit.com", "mail2.pyzit.com"]
result.details.has_spf     # True
result.details.spf_record  # "v=spf1 include:_spf.pyzit.com ~all"
result.details.has_dmarc   # True
result.details.dmarc_record # "v=DMARC1; p=reject; sp=reject"
```

**Response shape:**

```
DetailedResult
├── email              str
├── domain             str
├── is_disposable      bool
├── is_trusted         bool
├── is_privacy_relay   bool
├── relay_provider     str | None
├── provider_name      str | None
├── classification     str     — "trusted" | "clean" | "privacy_relay" | "suspicious" | "disposable"
├── reputation_score   int     — 0 (worst) to 100 (best)
├── risk_level         str     — "low" | "medium" | "high"
├── is_valid_format    bool
├── cached             bool
├── rule_applied       str | None
├── should_reject      bool    — shorthand: is_disposable or not is_trusted
├── should_flag        bool    — shorthand: classification in ("unknown", "suspicious")
├── has_mx             bool    — shorthand: details.has_mx
└── details            DetailedDetails
    ├── has_mx       bool
    ├── mx_records   list[str]
    ├── has_a        bool
    ├── a_records    list[str]
    ├── has_spf      bool
    ├── spf_record   str | None
    ├── has_dmarc    bool
    └── dmarc_record str | None
```

---

### `BulkResult` ← `bulk(emails: list[str])`

Validate multiple emails in a single API call. Uses `simple_quota`. Batch size depends on your plan (Free=10, Starter=25, Pro=50, Growth=75, Scale=100).

```python
result = client.bulk([
    "hi@pyzit.com",
    "user@mailnator.com",
    "user@privaterelay.appleid.com",
])

result.total                 # 3
result.status                # "mixed"
result.disposable_count      # 1
result.privacy_relay_count   # 1
result.flagged_domains       # ["mailnator.com"]

result.clean_emails()        # ["hi@pyzit.com", "user@privaterelay.appleid.com"]
result.disposable_emails()   # ["user@mailnator.com"]
result.privacy_relay_emails() # ["user@privaterelay.appleid.com"]
```

**Response shape:**

```
BulkResult
├── total                  int              — number of emails processed
├── status                 str              — "clean" | "disposable" | "privacy_relay" | "mixed"
├── disposable_count       int              — number of disposable emails
├── privacy_relay_count    int              — number of privacy relay emails
├── flagged_domains        list[str]        — unique disposable domains
├── results                list[BulkItemResult]
│   ├── email              str
│   ├── is_disposable      bool
│   ├── is_privacy_relay   bool
│   └── status             str
├── clean_emails()         list[str]        — emails where is_disposable=False
├── disposable_emails()    list[str]        — emails where is_disposable=True
└── privacy_relay_emails() list[str]        — emails where is_privacy_relay=True
```

---

## ◈ Async usage

`AsyncTempMailClient` is a drop-in replacement for async codebases.
The method signatures are identical — just add `await`.

```python
from tempmail_pyzit import AsyncTempMailClient

client = AsyncTempMailClient("YOUR_API_TOKEN")

# anywhere inside an async function:
result = await client.check("user@example.com")
result = await client.detailed("user@example.com")
result = await client.bulk(["a@x.com", "b@y.com"])
```

Both clients share the same response models, exceptions, and behaviour.
There is no functional difference other than `async/await`.

---

## ◈ Response models

All responses are fully typed [Pydantic v2](https://docs.pydantic.dev/) models.
You get autocomplete, runtime validation, and type safety for free.

```
tempmail_pyzit.models
│
├── CheckResult          ← client.check()
├── DetailedResult       ← client.detailed()
│   └── DetailedDetails  (DNS intelligence)
└── BulkResult           ← client.bulk()
    └── BulkItemResult
```

---

## ◈ Error handling

All SDK errors inherit from `PyzitError`, so you can catch everything
at one level or be specific.

```
PyzitError                    ← catch-all for any SDK error
├── AuthenticationError       ← HTTP 401 — bad or missing token
├── InsufficientScopeError    ← HTTP 403 — token lacks required scope
│   └── .required_scope       ← str, e.g. "tmd:basic" or "tmd:detailed"
├── QuotaExceededError        ← HTTP 402 — monthly quota exhausted
│   └── .quota_type           ← str, "simple" or "detailed"
├── BatchLimitExceededError   ← HTTP 400 — bulk request exceeds plan limit
│   ├── .max_allowed          ← int, plan's batch size limit
│   └── .attempted            ← int, emails attempted
├── ValidationError           ← HTTP 400 — malformed email or request
│   └── .field_errors         ← dict, field-specific errors
├── RateLimitError            ← HTTP 429 — rate limit exceeded
│   └── .retry_after          ← float, seconds to wait
├── APIError                  ← HTTP 5xx or unexpected status
│   ├── .status_code          ← int
│   └── .response_body        ← str, raw body for debugging
└── TimeoutError              ← request took too long
```

**Recommended pattern — catch specific errors:**

```python
from tempmail_pyzit import (
    TempMailClient,
    AuthenticationError,
    InsufficientScopeError,
    QuotaExceededError,
    BatchLimitExceededError,
    RateLimitError,
    APIError,
    TimeoutError,
    PyzitError,
)
import time

client = TempMailClient("YOUR_TOKEN")

try:
    result = client.check("user@example.com")

except AuthenticationError:
    # token is wrong — fail fast, don't retry
    raise SystemExit("Check your PYZIT_TOKEN environment variable.")

except InsufficientScopeError as e:
    # token lacks required scope
    print(f"Your API token lacks the '{e.required_scope}' scope.")

except QuotaExceededError as e:
    # monthly quota exhausted
    print(f"You've exceeded your monthly {e.quota_type} quota. Upgrade your plan.")

except BatchLimitExceededError as e:
    # bulk request exceeds plan limit
    print(f"Your plan allows max {e.max_allowed} emails per bulk request.")

except RateLimitError as e:
    # back off and retry
    time.sleep(e.retry_after)
    result = client.check("user@example.com")

except TimeoutError:
    # API too slow — decide how to handle in your app
    print("Pyzit API timed out — allowing email through.")

except APIError as e:
    # unexpected server error
    print(f"Unexpected error {e.status_code}: {e.response_body}")

except PyzitError:
    # fallback for any other SDK error
    print("Something went wrong with the Pyzit SDK.")
```

**Minimal pattern — just block disposables, ignore errors gracefully:**

```python
def is_allowed(email: str) -> bool:
    try:
        return not client.check(email).is_disposable
    except PyzitError:
        return True  # fail open — let the email through if API is down
```

---

## ◈ Framework integrations

### Django

```python
# validators.py
from django.core.exceptions import ValidationError
from tempmail_pyzit import TempMailClient, PyzitError
import os

_client = TempMailClient(os.environ["PYZIT_TOKEN"])

def validate_no_disposable_email(value: str) -> None:
    try:
        result = _client.check(value)
        if result.is_disposable:
            raise ValidationError(
                "Disposable email addresses are not allowed. "
                "Please use your real email."
            )
    except PyzitError:
        pass  # fail open if API is unreachable

# models.py
from django.db import models
from .validators import validate_no_disposable_email

class UserProfile(models.Model):
    email = models.EmailField(validators=[validate_no_disposable_email])
```

---

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from tempmail_pyzit import AsyncTempMailClient, PyzitError
import os

app = FastAPI()
client = AsyncTempMailClient(os.environ["PYZIT_TOKEN"])

@app.post("/register")
async def register(email: str):
    try:
        result = await client.check(email)
    except PyzitError:
        pass  # fail open
    else:
        if result.is_disposable:
            raise HTTPException(
                status_code=422,
                detail="Disposable email addresses are not permitted."
            )
    return {"status": "ok", "email": email}
```

---

### Flask

```python
from flask import Flask, request, jsonify
from tempmail_pyzit import TempMailClient, PyzitError
import os

app = Flask(__name__)
client = TempMailClient(os.environ["PYZIT_TOKEN"])

@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "")
    try:
        result = client.check(email)
        if result.is_disposable:
            return jsonify({"error": "Disposable emails not allowed."}), 422
    except PyzitError:
        pass  # fail open
    return jsonify({"status": "ok"})
```

---

## ◈ Configuration

Both `TempMailClient` and `AsyncTempMailClient` accept the same options:

```python
client = TempMailClient(
    api_token = "YOUR_TOKEN",   # required
    timeout   = 5.0,            # seconds, default 5.0
    base_url  = "https://api.pyzit.com",  # override for testing
    max_retries = 2,            # retry attempts for 429/5xx, default 2
    fail_open  = False,         # return clean on network errors, default False
)
```

| Parameter   | Type    | Default                                      | Description                        |
|-------------|---------|----------------------------------------------|------------------------------------|
| `api_token` | `str`   | —                                            | Your Pyzit API token (required)    |
| `timeout`   | `float` | `5.0`                                        | Request timeout in seconds         |
| `base_url`  | `str`   | `https://api.pyzit.com`                      | Override for local testing / mocks |
| `max_retries`| `int`   | `2`                                          | Retry attempts for 429/5xx errors  |
| `fail_open` | `bool`  | `False`                                      | Return clean result on network errors|

---

## ◈ Development

This project is built with [uv](https://github.com/astral-sh/uv).

```bash
# clone
git clone https://github.com/pyzit-org/temp-mail-detector-sdk-python.git
cd temp-mail-detector-sdk-python

# install all dev dependencies
uv sync --extra dev

# run tests (no real API calls — all HTTP is mocked)
uv run pytest -v

# lint
uv run ruff check . --fix
uv run ruff format .

# type check (strict mypy)
uv run mypy src/

# build distribution
uv build
```

**Project layout:**

```
src/tempmail_pyzit/
├── __init__.py        ← public API surface
├── exceptions.py      ← all custom error classes
├── models.py          ← pydantic response types
├── _http.py           ← shared transport (headers, error handling)
├── client.py          ← TempMailClient (sync)
└── async_client.py    ← AsyncTempMailClient (async)

tests/
├── conftest.py        ← shared fixtures
├── test_client.py     ← sync client tests
├── test_async_client.py
└── test_models.py
```

---

## ◈ Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## ◈ License

[MIT](LICENSE) © [Pyzit](https://pyzit.com)

---

<div align="center">

```
Built with care by the Pyzit team · https://pyzit.com
```

</div>
