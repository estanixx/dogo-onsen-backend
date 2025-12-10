import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from app.services.venue_account import VenueAccountService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_get_and_compute_balance():
    session = MagicMock()
    session.exec = AsyncMock()

    # list_accounts -> empty
    session.exec.return_value = DummyResult([])
    out = await VenueAccountService.list_accounts(session=session)
    assert out == []

    # get_current_account_for_room -> None if not found
    session.exec.return_value = DummyResult([])
    got = await VenueAccountService.get_current_account_for_room(1, session=session)
    assert got is None
