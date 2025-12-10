import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, date

from app.services.banquet import BanquetService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_tables_and_seats_and_availability():
    session = MagicMock()
    session.exec = AsyncMock()

    # list_tables -> empty
    session.exec.return_value = DummyResult([])
    res = await BanquetService.list_tables(session)
    assert res == []

    # list_seats with no tableId -> empty
    session.exec.return_value = DummyResult([])
    seats = await BanquetService.list_seats(None, session)
    assert seats == []

    # get_available_time_slots for past date -> should return []
    past = date(2000, 1, 1)
    slots = await BanquetService.get_available_time_slots("1", past, session)
    assert slots == []
