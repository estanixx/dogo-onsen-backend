import pytest
from unittest.mock import MagicMock, AsyncMock

from app.services.type_relation import TypeRelationService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


@pytest.mark.asyncio
async def test_list_create_get_update_delete_and_relation_between():
    session = MagicMock()
    session.exec = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()

    # list empty
    session.exec.return_value = DummyResult([])
    lst = await TypeRelationService.list_type_relations(session=session)
    assert lst == []

    # create returns an object (we won't validate fields)
    class In:
        def dict(self):
            return {"source_type_id": "a", "target_type_id": "b", "relation": "allow"}

    created = await TypeRelationService.create_type_relation(In(), session=session)
    assert created is not None

    # get_relation_between direct
    fake_tr = MagicMock()
    session.exec.side_effect = [DummyResult([fake_tr]), DummyResult([])]
    tr = await TypeRelationService.get_relation_between("a", "b", session=session)
    assert tr is fake_tr

    # try inverse
    session.exec.side_effect = [DummyResult([]), DummyResult([fake_tr])]
    tr2 = await TypeRelationService.get_relation_between("a", "b", session=session)
    assert tr2 is fake_tr

    # update/delete when not found
    session.exec.side_effect = None
    session.exec.return_value = DummyResult([])

    class Upd:
        def dict(self, exclude_unset=True):
            return {"relation": "forbidden"}

    u = await TypeRelationService.update_type_relation(1, Upd(), session=session)
    assert u is None

    d = await TypeRelationService.delete_type_relation(1, session=session)
    assert d is False
