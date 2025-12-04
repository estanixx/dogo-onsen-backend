import pytest
from app.services import InventoryOrderService


@pytest.mark.asyncio
async def test_list_inventory_items_empty(async_session_mock):
    items = await InventoryOrderService.list_inventory_orders(async_session_mock)
    assert isinstance(items, list)
    assert items == []
