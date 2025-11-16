from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.reservation import Reservation, ReservationCreate, ReservationUpdate

ReservationRouter = APIRouter()


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
