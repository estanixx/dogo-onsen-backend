import pytest
from app.services.employee import EmployeeService


def test_map_clerk_user_to_employee_payload():
    user = {
        "id": "clerk_1",
        "public_metadata": {"estado": "activo", "tareasAsignadas": [1, 2]},
        "email_addresses": [{"email_address": "a@b.com"}],
        "first_name": "Juan",
        "last_name": "Perez",
    }

    mapped = EmployeeService._map_clerk_user_to_employee_payload(user)
    assert mapped["clerkId"] == "clerk_1"
    assert mapped["estado"] == "activo"
    assert mapped["tareasAsignadas"] == ["1", "2"]
    assert mapped["email"] == "a@b.com"
