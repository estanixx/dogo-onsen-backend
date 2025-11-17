from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.reservation import Reservation, ReservationCreate, ReservationUpdate
from datetime import datetime, date, time, timedelta, timezone
from fastapi import Body

ReservationRouter = APIRouter()
from app.models.utils import DateRequest


@ReservationRouter.get("/", response_model=list[Reservation])
async def list_reservations(accountId: str | None = None, session: AsyncSession = Depends(get_session)):
    q = select(Reservation)
    if accountId:
        q = q.where(Reservation.accountId == accountId)
    result = await session.execute(q)
    return result.scalars().all()


@ReservationRouter.post("/", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(reservation: ReservationCreate, session: AsyncSession = Depends(get_session)):
    r = Reservation(**reservation.dict())
    session.add(r)
    await session.commit()
    await session.refresh(r)
    return r



@ReservationRouter.post("/banquet-by-date", response_model=list[Reservation])
async def get_banquet_reservations_for_date(payload: DateRequest = Body(...), session: AsyncSession = Depends(get_session)):
    """Return all reservations that have a seatId for the given date.

    The request body must be JSON: { "date": "YYYY-MM-DD" } or any ISO date/time string.
    The server treats the date as UTC date and returns reservations whose startTime
    falls within that UTC date (00:00:00 <= startTime < next day).
    """
    # parse date (accept YYYY-MM-DD or full ISO datetime)
    try:
        if len(payload.date) <= 10 and "-" in payload.date:
            d = date.fromisoformat(payload.date)
        else:
            d = datetime.fromisoformat(payload.date).date()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD or ISO datetime.")

    start_dt = datetime.combine(d, time.min).replace(tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=1)

    q = select(Reservation).where(Reservation.seatId != None).where(Reservation.startTime >= start_dt).where(Reservation.startTime < end_dt)
    result = await session.execute(q)
    return result.scalars().all()


@ReservationRouter.get("/{reservation_id}", response_model=Reservation)
async def get_reservation(reservation_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    return r


@ReservationRouter.put("/{reservation_id}", response_model=Reservation)
async def update_reservation(reservation_id: str, reservation: ReservationUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    data = reservation.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(r, key, value)

    session.add(r)
    await session.commit()
    await session.refresh(r)
    return r


@ReservationRouter.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(reservation_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Reservation).where(Reservation.id == reservation_id))
    r = result.scalars().first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")

    await session.delete(r)
    await session.commit()
    return None


