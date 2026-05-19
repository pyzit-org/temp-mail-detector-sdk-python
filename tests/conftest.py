import pytest

from tempmail_pyzit import AsyncTempMailClient, TempMailClient

FAKE_TOKEN = "test-token-xyz"


@pytest.fixture
def client() -> TempMailClient:
    return TempMailClient(FAKE_TOKEN)


@pytest.fixture
def async_client() -> AsyncTempMailClient:
    return AsyncTempMailClient(FAKE_TOKEN)
