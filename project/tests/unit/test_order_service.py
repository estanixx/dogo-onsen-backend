import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.order import OrderService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_get_and_redeem_order():
    session = MagicMock()
    session.exec = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    # list_orders -> empty
    session.exec.return_value = DummyResult([])
    lst = await OrderService.list_orders(session=session)
    assert lst == []

    # get_order -> not found
    session.exec.return_value = DummyResult([])
    got = await OrderService.get_order(1, session=session)
    assert got is None

    # redeem_order: create fake order with items
    item1 = MagicMock()
    item1.redeemed = False
    item2 = MagicMock()
    item2.redeemed = False
    fake_order = MagicMock()
    fake_order.items = [item1, item2]

    session.exec.return_value = DummyResult([fake_order])
    r = await OrderService.redeem_order(1, session=session)
    assert r is not None
    assert all(getattr(i, "redeemed", False) for i in r.items)
