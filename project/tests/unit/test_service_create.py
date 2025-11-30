import pytest
from app.services.service import ServiceService


@pytest.mark.asyncio
async def test_create_service_calls_session(async_session_mock):
    class SvcIn:
        def dict(self):
            return {'id': 's1', 'name': 'Servicio', 'description': 'desc', 'eiltRate': 10}

    svc = await ServiceService.create_service(SvcIn(), async_session_mock)
    assert async_session_mock.add.called
    assert async_session_mock.commit.called
    assert hasattr(svc, 'id')
