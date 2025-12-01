import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
from app.models import Reservation, ReservationCreate, ReservationUpdate
from app.services.reservation import ReservationService

@pytest.mark.asyncio
async def test_create_reservation(async_session_mock):
    reservation_in = ReservationCreate(
        accountId="acc_123",
        serviceId="svc_123",
        startTime=datetime.now(timezone.utc),
        endTime=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    
    # Mock session.add/commit/refresh
    async_session_mock.add = MagicMock()
    async_session_mock.commit = AsyncMock()
    async_session_mock.refresh = AsyncMock()
    
    result = await ReservationService.create_reservation(reservation_in, async_session_mock)
    
    assert result.accountId == "acc_123"
    assert result.serviceId == "svc_123"
    async_session_mock.add.assert_called_once()
    async_session_mock.commit.assert_called_once()
    async_session_mock.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_list_reservations_by_account(async_session_mock):
    # Override the side_effect from conftest to return our mock result
    mock_res_obj = Reservation(id="res_1", accountId="acc_123", serviceId="svc_1")
    
    # Create a mock result object that behaves like the SQLModel result
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_res_obj]
    
    # Set side_effect to return this mock result
    async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
    
    filters = {"accountId": "acc_123"}
    result = await ReservationService.list_reservations(filters, async_session_mock)
    
    assert len(result) == 1
    assert result[0].accountId == "acc_123"

@pytest.mark.asyncio
async def test_update_reservation_redeem(async_session_mock):
    # Mock get existing
    mock_res_obj = Reservation(id="res_1", isRedeemed=False)
    
    mock_result = MagicMock()
    mock_result.first.return_value = mock_res_obj
    
    # Override side_effect
    async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
    
    async_session_mock.add = MagicMock()
    async_session_mock.commit = AsyncMock()
    async_session_mock.refresh = AsyncMock()
    
    update_data = ReservationUpdate(isRedeemed=True)
    result = await ReservationService.update_reservation("res_1", update_data, async_session_mock)
    
    assert result is not None
    assert result.isRedeemed is True
    async_session_mock.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_reservation(async_session_mock):
    mock_res_obj = Reservation(id="res_1")
    
    mock_result = MagicMock()
    mock_result.first.return_value = mock_res_obj
    
    # Override side_effect
    async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
    
    async_session_mock.delete = AsyncMock()
    async_session_mock.commit = AsyncMock()
    
    result = await ReservationService.delete_reservation("res_1", async_session_mock)
    
    assert result is True
    async_session_mock.delete.assert_called_once_with(mock_res_obj)
    async_session_mock.commit.assert_called_once()
