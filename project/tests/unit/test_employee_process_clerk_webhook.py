import pytest
from app.services.employee import EmployeeService


@pytest.mark.asyncio
async def test_process_clerk_webhook_creates_new(async_session_mock):
    payload = {
        'data': {'object': {'id': 'clerk_123', 'public_metadata': {'estado': 'activo'}, 'email_addresses': [{'email_address': 'a@b.com'}], 'first_name': 'A', 'last_name': 'B'}}
    }

    res = await EmployeeService.process_clerk_webhook(payload, async_session_mock)
    assert res.get('ok') is True
    assert res.get('action') in ('created', 'updated')
