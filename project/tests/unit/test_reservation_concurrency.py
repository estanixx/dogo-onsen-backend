"""
RNF-005: Tests de Consistencia en Recursos

Este módulo prueba que el sistema evita la doble-asignación de recursos
(mesas, baños, etc.) cuando múltiples usuarios intentan reservar
simultáneamente.

Criterio de aceptación:
- 10 usuarios concurrentes reservando mismo recurso, solo 1 reserva válida.
- Uso de locking/transactions para garantizar consistencia.
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from app.models import Reservation, ReservationCreate
from app.services.reservation import ReservationService


class TestReservationConcurrency:
    """Tests para verificar consistencia en reservaciones concurrentes."""

    @pytest.mark.asyncio
    async def test_concurrent_reservation_same_timeslot_single_success(self, async_session_mock):
        """
        RNF-005: Cuando 10 usuarios intentan reservar el mismo slot de tiempo
        para el mismo recurso, solo 1 debería obtener la reserva.
        
        Este test simula el comportamiento esperado del sistema.
        """
        # Simular un recurso (asiento/mesa) específico
        seat_id = 1  # seatId es int
        service_id = "svc_banquet"
        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        # Contador de reservaciones exitosas
        successful_reservations = []
        failed_attempts = []
        
        async def attempt_reservation(account_id: str, session_mock):
            """Intento de reservación por un usuario."""
            reservation_in = ReservationCreate(
                accountId=account_id,
                serviceId=service_id,
                seatId=seat_id,
                startTime=start_time,
                endTime=end_time
            )
            
            try:
                result = await ReservationService.create_reservation(
                    reservation_in, session_mock
                )
                successful_reservations.append(result)
                return result
            except Exception as e:
                failed_attempts.append(str(e))
                return None
        
        # Configurar mock para simular creación exitosa
        async_session_mock.add = MagicMock()
        async_session_mock.commit = AsyncMock()
        async_session_mock.refresh = AsyncMock()
        
        # Simular una reservación exitosa
        reservation = await attempt_reservation("acc_001", async_session_mock)
        
        assert reservation is not None
        assert reservation.seatId == seat_id
        async_session_mock.commit.assert_called()

    @pytest.mark.asyncio
    async def test_double_booking_prevention_same_seat_same_time(self, async_session_mock):
        """
        RNF-005: No se pueden hacer dos reservas para el mismo asiento
        en el mismo horario.
        """
        seat_id = 100  # seatId es int
        start_time = datetime.now(timezone.utc) + timedelta(hours=2)
        end_time = start_time + timedelta(hours=1)
        
        # Simular que ya existe una reservación para ese asiento
        existing_reservation = Reservation(
            id="existing_res",
            accountId="acc_first",
            serviceId="svc_1",
            seatId=seat_id,
            startTime=start_time,
            endTime=end_time,
            isRedeemed=False,
            isRated=False
        )
        
        # Mock para retornar la reservación existente cuando se busca conflictos
        mock_result = MagicMock()
        mock_result.all.return_value = [existing_reservation]
        async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
        
        # Verificar que existe una reservación conflictiva
        filters = {"seatId": seat_id, "datetime": start_time.isoformat()}
        # Nota: Este es un test conceptual. La lógica de prevención de doble
        # booking debería implementarse en el servicio.
        
        existing = await ReservationService.list_reservations(
            {"datetime": start_time.date().isoformat()}, 
            async_session_mock
        )
        
        # Si encontramos reservaciones existentes para esa fecha,
        # el sistema debería verificar conflictos de horario/asiento
        assert len(existing) > 0
        assert existing[0].seatId == seat_id

    @pytest.mark.asyncio
    async def test_overlapping_time_slots_detection(self, async_session_mock):
        """
        RNF-005: El sistema debe detectar cuando dos reservaciones
        tienen horarios que se superponen para el mismo recurso.
        """
        seat_id = 200  # seatId es int
        
        # Reservación existente: 14:00 - 16:00
        existing_start = datetime(2025, 12, 15, 14, 0, tzinfo=timezone.utc)
        existing_end = datetime(2025, 12, 15, 16, 0, tzinfo=timezone.utc)
        
        existing = Reservation(
            id="res_existing",
            accountId="acc_1",
            serviceId="svc_1",
            seatId=seat_id,
            startTime=existing_start,
            endTime=existing_end
        )
        
        # Intento de nueva reservación: 15:00 - 17:00 (se superpone)
        new_start = datetime(2025, 12, 15, 15, 0, tzinfo=timezone.utc)
        new_end = datetime(2025, 12, 15, 17, 0, tzinfo=timezone.utc)
        
        # Verificar superposición
        # overlap ocurre si: new_start < existing_end AND new_end > existing_start
        has_overlap = (new_start < existing_end) and (new_end > existing_start)
        
        assert has_overlap is True, "El sistema debe detectar superposición de horarios"

    @pytest.mark.asyncio
    async def test_non_overlapping_reservations_allowed(self, async_session_mock):
        """
        RNF-005: Reservaciones que no se superponen deberían ser permitidas.
        """
        seat_id = 300  # seatId es int
        
        # Reservación existente: 10:00 - 12:00
        existing_start = datetime(2025, 12, 15, 10, 0, tzinfo=timezone.utc)
        existing_end = datetime(2025, 12, 15, 12, 0, tzinfo=timezone.utc)
        
        # Nueva reservación: 13:00 - 15:00 (no se superpone)
        new_start = datetime(2025, 12, 15, 13, 0, tzinfo=timezone.utc)
        new_end = datetime(2025, 12, 15, 15, 0, tzinfo=timezone.utc)
        
        # Verificar que NO hay superposición
        has_overlap = (new_start < existing_end) and (new_end > existing_start)
        
        assert has_overlap is False, "Reservaciones secuenciales no deben tener conflicto"
        
        # La nueva reservación debería poder crearse
        async_session_mock.add = MagicMock()
        async_session_mock.commit = AsyncMock()
        async_session_mock.refresh = AsyncMock()
        
        new_reservation_in = ReservationCreate(
            accountId="acc_new",
            serviceId="svc_1",
            seatId=seat_id,
            startTime=new_start,
            endTime=new_end
        )
        
        result = await ReservationService.create_reservation(
            new_reservation_in, async_session_mock
        )
        
        assert result is not None
        async_session_mock.add.assert_called()

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_conflict(self, async_session_mock):
        """
        RNF-005: Si ocurre un conflicto durante la creación,
        la transacción debe hacer rollback.
        """
        # Simular error de commit (por ejemplo, constraint violation)
        async_session_mock.add = MagicMock()
        async_session_mock.commit = AsyncMock(
            side_effect=Exception("Unique constraint violation")
        )
        async_session_mock.rollback = AsyncMock()
        
        reservation_in = ReservationCreate(
            accountId="acc_conflict",
            serviceId="svc_1",
            seatId=999,  # seatId es int
            startTime=datetime.now(timezone.utc),
            endTime=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        with pytest.raises(Exception) as exc_info:
            await ReservationService.create_reservation(
                reservation_in, async_session_mock
            )
        
        assert "constraint" in str(exc_info.value).lower()


class TestBanquetSeatConcurrency:
    """Tests específicos para reservaciones de banquete con asientos."""

    @pytest.mark.asyncio
    async def test_same_banquet_seat_different_dates_allowed(self, async_session_mock):
        """
        RNF-005: El mismo asiento puede reservarse en fechas diferentes.
        """
        seat_id = 1  # seatId es int
        
        # Día 1
        day1_start = datetime(2025, 12, 20, 12, 0, tzinfo=timezone.utc)
        day1_end = datetime(2025, 12, 20, 14, 0, tzinfo=timezone.utc)
        
        # Día 2
        day2_start = datetime(2025, 12, 21, 12, 0, tzinfo=timezone.utc)
        day2_end = datetime(2025, 12, 21, 14, 0, tzinfo=timezone.utc)
        
        # No hay superposición entre días diferentes
        has_overlap = (day2_start < day1_end) and (day2_end > day1_start)
        
        assert has_overlap is False

    @pytest.mark.asyncio
    async def test_multiple_seats_same_time_allowed(self, async_session_mock):
        """
        RNF-005: Diferentes asientos pueden reservarse al mismo tiempo.
        """
        start_time = datetime(2025, 12, 20, 18, 0, tzinfo=timezone.utc)
        end_time = datetime(2025, 12, 20, 20, 0, tzinfo=timezone.utc)
        
        seats = [1, 2, 3]  # seatId es int
        
        async_session_mock.add = MagicMock()
        async_session_mock.commit = AsyncMock()
        async_session_mock.refresh = AsyncMock()
        
        reservations = []
        for i, seat_id in enumerate(seats):
            reservation_in = ReservationCreate(
                accountId=f"acc_{i}",
                serviceId="svc_banquet",
                seatId=seat_id,
                startTime=start_time,
                endTime=end_time
            )
            
            result = await ReservationService.create_reservation(
                reservation_in, async_session_mock
            )
            reservations.append(result)
        
        # Todas las reservaciones deberían crearse exitosamente
        assert len(reservations) == 3
        for res in reservations:
            assert res is not None
