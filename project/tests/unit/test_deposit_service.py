import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.deposit import DepositService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_and_create_get_update_delete_deposit():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    session.exec.return_value = DummyResult([])
    res = await DepositService.list_deposits(session=session)
    assert res == []

    # list_deposits_for_account
    session.exec.return_value = DummyResult([])
    res2 = await DepositService.list_deposits_for_account("a1", session=session)
    assert res2 == []

    # get_deposit not found
    g = await DepositService.get_deposit("no", session=session)
    assert g is None

    # update/delete when not found
    u = await DepositService.update_deposit("no", MagicMock(), session=session)
    assert u is None
    d = await DepositService.delete_deposit("no", session=session)
    assert d is False
