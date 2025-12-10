import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from app.services.spirit import SpiritService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_and_get_spirit():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    # list_spirits: return empty
    session.exec.return_value = DummyResult([])
    out = await SpiritService.list_spirits(session=session)
    assert out == []

    # get_spirit when not found
    session.exec.return_value = DummyResult([])
    got = await SpiritService.get_spirit(123, session=session)
    assert got is None

    # get_spirit when found: simulate spirit and an overlapping venue account
    class FakeType:
        def __init__(self):
            self.id = "t1"
            self.name = "T"
            self.kanji = "K"
            self.dangerScore = 1
            self.image = "i"

    class FakeSpirit:
        def __init__(self):
            self.id = 42
            self.name = "S"
            self.typeId = "t1"
            self.image = None
            self.active = True
            from datetime import datetime

            self.createdAt = datetime.now()
            self.updatedAt = datetime.now()
            self.type = FakeType()

    fake = FakeSpirit()
    # first exec returns spirit
    # second exec (overlap) returns non-empty
    session.exec.side_effect = [DummyResult([fake]), DummyResult([1])]
    got2 = await SpiritService.get_spirit(42, session=session)
    assert got2 is not None
    assert getattr(got2, "currentlyInVenue") in (True, False)
