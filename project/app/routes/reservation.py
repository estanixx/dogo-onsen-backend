from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Reservation, ReservationCreate, ReservationUpdate
from datetime import datetime, date, time, timedelta, timezone
from fastapi import Body

from app.services import ReservationService
from app.deps.device_cookie import get_device_config, DeviceConfig

ReservationRouter = APIRouter()
from app.models.utils import DateRequest


@ReservationRouter.get("/", response_model=list[Reservation])
async def list_reservations(
    accountId: str | None = None,
    session: AsyncSession = Depends(get_session),
    device_config: DeviceConfig | None = Depends(get_device_config),
):
    return await ReservationService.list_reservations(accountId, session)


@ReservationRouter.post("/", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(reservation: ReservationCreate, session: AsyncSession = Depends(get_session)):
    return await ReservationService.create_reservation(reservation, session)



@ReservationRouter.post("/banquet-by-date", response_model=list[Reservation])
async def get_banquet_reservations_for_date(payload: DateRequest = Body(...), session: AsyncSession = Depends(get_session)):
    """Return all reservations that have a seatId for the given date.

    The request body must be JSON: { "date": "YYYY-MM-DD" } or any ISO date/time string.
    The server treats the date as UTC date and returns reservations whose startTime
    falls within that UTC date (00:00:00 <= startTime < next day).
    """
    try:
        return await ReservationService.get_banquet_reservations_for_date(payload, session)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD or ISO datetime.")


@ReservationRouter.get("/{reservation_id}", response_model=Reservation)
async def get_reservation(reservation_id: str, session: AsyncSession = Depends(get_session)):
    r = await ReservationService.get_reservation(reservation_id, session)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return r


@ReservationRouter.put("/{reservation_id}", response_model=Reservation)
async def update_reservation(reservation_id: str, reservation: ReservationUpdate, session: AsyncSession = Depends(get_session)):
    r = await ReservationService.update_reservation(reservation_id, reservation, session)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return r


@ReservationRouter.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(reservation_id: str, session: AsyncSession = Depends(get_session)):
    ok = await ReservationService.delete_reservation(reservation_id, session)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return None


