import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException

from app.services.employee import EmployeeService


class DummyResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


def test_extract_and_map_clerk_payload():
    # empty payload
    assert EmployeeService._extract_user_from_payload({}) == {}

    # payload with data.object
    p = {"data": {"object": {"id": "u1"}}}
    assert EmployeeService._extract_user_from_payload(p).get("id") == "u1"

    # map clerk user to employee payload
    user = {
        "id": "c1",
        "first_name": "F",
        "last_name": "L",
        "email_addresses": [{"email_address": "a@e.com"}],
        "public_metadata": {"accessStatus": "activo", "tareasAsignadas": [1, 2]},
    }
    mapped = EmployeeService._map_clerk_user_to_employee_payload(user)
    assert mapped["clerkId"] == "c1"
    assert mapped["email"] == "a@e.com"


@pytest.mark.asyncio
async def test_ensure_clerk_id_unique_raises():
    session = MagicMock()
    session.exec = AsyncMock()

    # simulate existing employee
    session.exec.return_value = DummyResult([{"clerkId": "c1"}])

    with pytest.raises(HTTPException):
        await EmployeeService._ensure_clerk_id_is_unique("c1", session=session)


import pytest
from app.services.employee import EmployeeService


def test_map_clerk_user_to_employee_payload():
    user = {
        "id": "clerk_1",
        "public_metadata": {"accessStatus": "approved", "tareasAsignadas": [1, 2]},
        "email_addresses": [{"email_address": "a@b.com"}],
        "first_name": "Juan",
        "last_name": "Perez",
    }

    mapped = EmployeeService._map_clerk_user_to_employee_payload(user)
    assert mapped["clerkId"] == "clerk_1"
    assert mapped["estado"] == "approved"
    assert mapped["tareasAsignadas"] == ["1", "2"]
    assert mapped["email"] == "a@b.com"
