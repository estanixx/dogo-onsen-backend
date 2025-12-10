import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.item import ItemService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_and_quantity_and_update_delete_item():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    # list_items -> returns empty list
    session.exec.return_value = DummyResult([])
    res = await ItemService.list_items(session=session)
    assert res == []

    # list_items_with_quantity: we need to simulate several exec calls
    # call sequence: items_res, inv_q, res_q, int_q
    # items: one item with id=1
    item = MagicMock()
    item.id = 1
    item.name = "I1"
    item.image = None
    item.unit = "u"

    inv_rows = []
    res_rows = []
    intakes = []

    session.exec.side_effect = [
        DummyResult([item]),
        DummyResult(inv_rows),
        DummyResult(res_rows),
        DummyResult(intakes),
    ]

    qtys = await ItemService.list_items_with_quantity(session=session)
    assert isinstance(qtys, list)

    # clear side_effect and set exec to return empty for subsequent calls
    session.exec.side_effect = None
    # update_item/delete_item when not found
    session.exec.return_value = DummyResult([])

    class Upd:
        def dict(self, exclude_unset=True):
            return {"name": "New"}

    upd = await ItemService.update_item(999, Upd(), session=session)
    assert upd is None

    d = await ItemService.delete_item(999, session=session)
    assert d is False
