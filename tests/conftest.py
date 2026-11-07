import asyncio

import pytest

from tempmail_pyzit import AsyncTempMailClient, TempMailClient

FAKE_TOKEN = "test-token-xyz"


@pytest.fixture(autouse=True)
def no_sleep_in_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock time.sleep and asyncio.sleep so retry tests run instantly without delay."""
    import time

    monkeypatch.setattr(time, "sleep", lambda *_: None)

    async def _mock_sleep(*_: object) -> None:
        pass

    monkeypatch.setattr(asyncio, "sleep", _mock_sleep)


@pytest.fixture
def client() -> TempMailClient:
    return TempMailClient(FAKE_TOKEN)


@pytest.fixture
def async_client() -> AsyncTempMailClient:
    return AsyncTempMailClient(FAKE_TOKEN)
