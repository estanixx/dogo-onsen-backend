import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.spirit_type import SpiritTypeService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_create_get_update_delete_spirit_type():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    session.exec.return_value = DummyResult([])
    res = await SpiritTypeService.list_spirit_types(session=session)
    assert res == []

    class In:
        def dict(self):
            return {"id": "t1", "name": "T"}

    created = await SpiritTypeService.create_spirit_type(In(), session=session)
    assert getattr(created, "id", None) is not None

    # get returns None when not found
    session.exec.return_value = DummyResult([])
    g = await SpiritTypeService.get_spirit_type("no", session=session)
    assert g is None

    # update/delete not found
    session.exec.return_value = DummyResult([])

    class Upd:
        def dict(self, exclude_unset=True):
            return {"name": "New"}

    u = await SpiritTypeService.update_spirit_type("no", Upd(), session=session)
    assert u is None
    d = await SpiritTypeService.delete_spirit_type("no", session=session)
    assert d is False
