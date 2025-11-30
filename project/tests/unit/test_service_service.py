import pytest
from app.services.service import ServiceService


@pytest.mark.asyncio
async def test_get_available_time_slots_empty(async_session_mock):
    # No reservations -> should return TIME_SLOTS length
    slots = await ServiceService.get_available_time_slots('svc-1', '2025-11-30', async_session_mock)
    from app.core.constants import TIME_SLOTS

    assert isinstance(slots, list)
    assert len(slots) == len(TIME_SLOTS)
