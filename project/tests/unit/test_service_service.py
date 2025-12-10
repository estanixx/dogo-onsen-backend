import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.service import ServiceService
from app.models.service import ServiceCreate


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_and_create_and_get_update_delete_service():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    # list_services -> return empty
    session.exec.return_value = DummyResult([])
    res = await ServiceService.list_services(session=session)
    assert res == []

    # create_service -> returns created object with fields set
    svc_in = ServiceCreate(name="S1", eiltRate=12.5)
    created = await ServiceService.create_service(svc_in, session=session)
    assert created.name == "S1"
    assert created.eiltRate == 12.5

    # get_service -> when not found returns None
    session.exec.return_value = DummyResult([])
    got = await ServiceService.get_service("no-id", session=session)
    assert got is None

    # simulate existing service for update/delete
    fake_svc = MagicMock()
    fake_svc.id = "svc-1"
    fake_svc.name = "Old"
    fake_svc.eiltRate = 1.0
    session.exec.return_value = DummyResult([fake_svc])

    # update_service
    class _Upd:
        def dict(self, exclude_unset=True):
            return {"name": "New"}

    updated = await ServiceService.update_service("svc-1", _Upd(), session=session)
    assert updated is not None
    assert getattr(updated, "name") == "New"

    # delete_service returns True when found
    session.exec.return_value = DummyResult([fake_svc])
    ok = await ServiceService.delete_service("svc-1", session=session)
    assert ok is True

    # delete_service returns False when not found
    session.exec.return_value = DummyResult([])
    ok2 = await ServiceService.delete_service("missing", session=session)
    assert ok2 is False


import pytest
from app.services.service import ServiceService


@pytest.mark.asyncio
async def test_get_available_time_slots_empty(async_session_mock):
    # No reservations -> should return TIME_SLOTS length
    slots = await ServiceService.get_available_time_slots(
        "svc-1", "2025-11-30", async_session_mock
    )
    from app.core.constants import TIME_SLOTS

    assert isinstance(slots, list)
    assert len(slots) == len(TIME_SLOTS)
