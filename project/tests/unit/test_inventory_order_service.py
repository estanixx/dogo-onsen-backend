import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.inventory_order import InventoryOrderService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_create_get_update_delete_inventory_order():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    session.exec.return_value = DummyResult([])
    lst = await InventoryOrderService.list_inventory_orders(session=session)
    assert lst == []

    # get not found
    g = await InventoryOrderService.get_inventory_order("no", session=session)
    assert g is None

    # update/delete not found
    u = await InventoryOrderService.update_inventory_order(
        "no", MagicMock(), session=session
    )
    assert u is None
    d = await InventoryOrderService.delete_inventory_order("no", session=session)
    assert d is False
