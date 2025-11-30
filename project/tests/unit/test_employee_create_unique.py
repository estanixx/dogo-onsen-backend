import pytest
from fastapi import HTTPException
from app.services.employee import EmployeeService


@pytest.mark.asyncio
async def test_create_employee_raises_if_clerk_exists(async_session_mock):
    class Dummy:
        def __init__(self):
            pass

    # Simulate existing clerk found by select -> first() returns an object
    async def fake_exec(q):
        m = type('M', (), {})()
        m.first = lambda: True
        m.all = lambda: []
        return m

    async_session_mock.exec.side_effect = fake_exec

    employee_in = type('E', (), {'clerkId': 'c1', 'dict': lambda self: {'clerkId': 'c1'}})()

    with pytest.raises(HTTPException):
        await EmployeeService.create_employee(employee_in, async_session_mock)
