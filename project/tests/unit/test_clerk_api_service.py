import pytest
import os
from unittest.mock import patch

from app.services.clerk_api import ClerkAPIService


def test_get_clerk_secret_key_missing():
    # Ensure ENV var missing raises
    if "CLERK_SECRET_KEY" in os.environ:
        del os.environ["CLERK_SECRET_KEY"]

    with pytest.raises(ValueError):
        ClerkAPIService._get_clerk_secret_key()


def test_extract_user_info():
    data = {
        "first_name": "A",
        "last_name": "B",
        "email_addresses": [{"email_address": "a@b.com"}],
    }
    out = ClerkAPIService.extract_user_info(data)
    assert out["firstName"] == "A"
    assert out["lastName"] == "B"
    assert out["email"] == "a@b.com"


@pytest.mark.asyncio
async def test_get_user_handles_errors(monkeypatch):
    # set a secret to pass env check
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test")

    # Patch httpx.AsyncClient to simulate non-200 response
    class DummyResp:
        status_code = 500
        text = "err"

        def json(self):
            return {}

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *args, **kwargs):
            return DummyResp()

    with patch("app.services.clerk_api.httpx.AsyncClient", return_value=DummyClient()):
        out = await ClerkAPIService.get_user("u1")
        assert out is None
