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

> **Tip:** Store your token in an environment variable, never hard-code it.
> ```python
> import os
> client = TempMailClient(os.environ["PYZIT_TOKEN"])
> ```

---

## ◈ API tiers

Three endpoints, three plan levels. Use only what you need.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ENDPOINT OVERVIEW                           │
├──────────────────┬─────────────┬──────────────────────────────────┤
│  Method          │  Plan       │  What you get                    │
├──────────────────┼─────────────┼──────────────────────────────────┤
│  client.check()  │  Free       │  is_disposable + status          │
│  client.detailed()│  Pro       │  DNS, signals, risk score, reco  │
│  client.bulk()   │  Business   │  Up to 100 emails, one request   │
└──────────────────┴─────────────┴──────────────────────────────────┘
```

---

## ◈ All methods

### `CheckResult` ← `check(email: str)`

The fastest check. One email in, one decision out. **Free tier.**

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

Full forensic analysis. DNS records, SMTP probing, reputation scoring,
domain age, signal breakdown. **Pro tier.**

```python
result = client.detailed("suspicious@new-domain.io")

result.risk_level       # "high"
result.recommendation   # "reject"
result.reputation_score # 0.0
result.should_reject    # True  (convenience property)

# DNS intelligence
result.details.dns_intelligence.has_mx      # False
result.details.dns_intelligence.has_spf     # False

# Signal breakdown
result.details.signals.negative  # ["no_mx_records", "new_domain", ...]
result.details.signals.positive  # []

# Domain stability
result.details.stability.domain_age_days  # 0
result.details.stability.is_new_domain    # True
```

**Response shape:**

```
DetailedResult
├── email              str
├── domain             str
├── is_disposable      bool
├── status             str
├── reputation_score   float   — 0.0 (worst) to 1.0 (best)
├── risk_level         str     — "low" | "medium" | "high"
├── recommendation     str     — "accept" | "review" | "reject"
├── should_reject      bool    — shorthand: recommendation == "reject"
└── details
    ├── reputation
    │   ├── reputation_score      float
    │   ├── is_disposable         bool
    │   ├── disposable_confidence float
    │   ├── risk_level            str
    │   └── recommendation        str
    ├── signals
    │   ├── positive   list[str]  — trust signals
    │   ├── negative   list[str]  — risk signals
    │   └── neutral    list[str]  — ambiguous signals
    ├── dns_intelligence
    │   ├── has_mx       bool
    │   ├── mx_records   list[str]
    │   ├── has_a_record bool
    │   ├── has_spf      bool
    │   ├── has_dmarc    bool
    │   └── error        str | None
    └── stability
        ├── stability_score   float
        ├── domain_age_days   int
        ├── is_new_domain     bool
        └── risk_factors      list[str]
```

---

### `BulkResult` ← `bulk(emails: list[str])`

Validate up to 100 emails in a single API call. **Business tier.**

```python
result = client.bulk([
    "hi@pyzit.com",
    "cyz@temp-mail.org",
    "user@mailnator.com",
])

result.processed          # 3
result.results            # {"hi@pyzit.com": False, "cyz@temp-mail.org": True, ...}

result.disposable_emails() # ["cyz@temp-mail.org", "user@mailnator.com"]
result.clean_emails()      # ["hi@pyzit.com"]
```

**Response shape:**

```
BulkResult
├── results             dict[str, bool]  — {email: is_disposable}
├── processed           int              — number of emails processed
├── disposable_emails() list[str]        — emails where is_disposable=True
└── clean_emails()      list[str]        — emails where is_disposable=False
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
│   └── DetailedDetails
│       ├── ReputationDetail
│       ├── Signals
│       ├── DnsIntelligence
│       └── StabilityInfo
└── BulkResult           ← client.bulk()
```

---

## ◈ Error handling

All SDK errors inherit from `PyzitError`, so you can catch everything
at one level or be specific.

```
PyzitError                    ← catch-all for any SDK error
├── AuthenticationError       ← HTTP 401 — bad or missing token
├── PlanRequiredError         ← HTTP 402/403 — need a higher plan
│   └── .required_plan        ← str, e.g. "pro" or "business"
├── RateLimitError            ← HTTP 429 — slow down
│   └── .retry_after          ← int, seconds to wait
├── APIError                  ← any other non-2xx response
│   ├── .status_code          ← int
│   └── .response_body        ← str, raw body for debugging
└── TimeoutError              ← request took too long
```

**Recommended pattern — catch specific errors:**

```python
from tempmail_pyzit import (
    TempMailClient,
    AuthenticationError,
    PlanRequiredError,
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

except PlanRequiredError as e:
    # you called an endpoint above your plan
    print(f"Upgrade to {e.required_plan} to use this feature.")

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
    timeout   = 10.0,           # seconds, default 10.0
    base_url  = "https://api-tempmail.pyzit.com/v1",  # override for testing
)
```

| Parameter   | Type    | Default                                      | Description                        |
|-------------|---------|----------------------------------------------|------------------------------------|
| `api_token` | `str`   | —                                            | Your Pyzit API token (required)    |
| `timeout`   | `float` | `10.0`                                       | Request timeout in seconds         |
| `base_url`  | `str`   | `https://api-tempmail.pyzit.com/v1`          | Override for local testing / mocks |

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
