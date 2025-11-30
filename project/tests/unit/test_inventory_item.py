import pytest
from app.services.inventory_item import InventoryItemService


@pytest.mark.asyncio
async def test_list_inventory_items_empty(async_session_mock):
    items = await InventoryItemService.list_inventory_items(async_session_mock)
    assert isinstance(items, list)
    assert items == []
