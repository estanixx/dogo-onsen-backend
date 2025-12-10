import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, date

from app.services.reservation import ReservationService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_create_get_update_delete_reservation():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    # list_reservations with no filters
    session.exec.return_value = DummyResult([])
    out = await ReservationService.list_reservations(None, session=session)
    assert out == []

    # create_reservation: pass an object with model_dump
    class In:
        def model_dump(self):
            return {"id": "r1"}

    created = await ReservationService.create_reservation(In(), session=session)
    assert created.id == "r1"

    # get_reservation -> not found
    session.exec.return_value = DummyResult([])
    got = await ReservationService.get_reservation("no", session=session)
    assert got is None

    # update_reservation -> when not found returns None
    session.exec.return_value = DummyResult([])
    upd = await ReservationService.update_reservation("no", In(), session=session)
    assert upd is None

    # delete_reservation -> when not found returns False
    session.exec.return_value = DummyResult([])
    d = await ReservationService.delete_reservation("no", session=session)
    assert d is False
