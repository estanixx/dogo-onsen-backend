import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.private_venue import PrivateVenueService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_private_venues_and_today_occupancy_rate():
    session = MagicMock()
    session.exec = AsyncMock()

    # list_private_venues fallback
    session.exec.return_value = DummyResult([])
    res = await PrivateVenueService.list_private_venues(None, session=session)
    assert res == []

    # today_occupancy_rate with no venues -> 0.0
    session.exec.return_value = DummyResult([])
    rate = await PrivateVenueService.today_occupancy_rate(session=session)
    assert rate == 0.0
