import pytest
from app.services.inventory_item import InventoryOrderService


@pytest.mark.asyncio
async def test_create_inventory_item_calls_session(async_session_mock):
    class ItemIn:
        def dict(self):
            return {"id": "x", "name": "Test", "quantity": 1, "unit": "u"}

    item = await InventoryOrderService.create_inventory_item(
        ItemIn(), async_session_mock
    )
    # session.add should have been called
    assert async_session_mock.add.called
    assert async_session_mock.commit.called
    assert hasattr(item, "id")
