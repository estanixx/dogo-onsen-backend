import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.item_intake import ItemIntakeService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_create_get_delete_item_intake():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    session.exec.return_value = DummyResult([])
    res = await ItemIntakeService.list_item_intakes(session=session)
    assert res == []

    class In:
        def dict(self):
            return {"id": 1, "quantity": 2}

    created = await ItemIntakeService.create_item_intake(In(), session=session)
    assert getattr(created, "id", None) is not None

    session.exec.return_value = DummyResult([])
    g = await ItemIntakeService.get_item_intake(999, session=session)
    assert g is None

    d = await ItemIntakeService.delete_item_intake(999, session=session)
    assert d is False
