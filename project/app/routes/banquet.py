from datetime import date, datetime, time, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from fastapi import Body
from app.models.utils import DateTimeRequest
from app.db import get_session
from app.models import (
    BanquetTable,
    BanquetTableCreate,
    BanquetTableUpdate,
    BanquetSeat,
    BanquetSeatCreate,
    BanquetSeatUpdate,
    BanquetTableRead,
    BanquetSeatRead,
    AvailableBanquetTableRead,
)
from app.services import BanquetService

BanquetRouter = APIRouter()


@BanquetRouter.get("/table/", response_model=List[BanquetTableRead])
async def list_tables(session: AsyncSession = Depends(get_session)):
    return await BanquetService.list_tables(session)


@BanquetRouter.post(
    "/table/available/{spirit_id}", response_model=List[AvailableBanquetTableRead]
)
async def list_available_seats(
    spirit_id: str,
    payload: DateTimeRequest = Body(...),
    session: AsyncSession = Depends(get_session),
):
    s = getattr(payload, "datetime", None) or getattr(payload, "date", None)
    if not s:
        raise ValueError("missing datetime")

    try:
        start_dt = datetime.fromisoformat(s)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD or ISO datetime.",
        )
    except Exception:
        d = date.fromisoformat(s)
        start_dt = datetime.combine(d, time.min)

    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    else:
        start_dt = start_dt.astimezone(timezone.utc)

    return await BanquetService.list_available_seats(spirit_id, start_dt, session)


@BanquetRouter.post(
    "/table/", response_model=BanquetTableRead, status_code=status.HTTP_201_CREATED
)
async def create_table(
    table: BanquetTableCreate, session: AsyncSession = Depends(get_session)
):
    return await BanquetService.create_table(table, session)


@BanquetRouter.get("/table/{table_id}", response_model=BanquetTableRead)
async def get_table(table_id: str, session: AsyncSession = Depends(get_session)):
    t = await BanquetService.get_table(table_id, session)
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Table not found"
        )
    return t


@BanquetRouter.put("/table/{table_id}", response_model=BanquetTableRead)
async def update_table(
    table_id: str,
    table: BanquetTableUpdate,
    session: AsyncSession = Depends(get_session),
):
    t = await BanquetService.update_table(table_id, table, session)
    if not t:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Table not found"
        )
    return t


@BanquetRouter.delete("/table/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(table_id: str, session: AsyncSession = Depends(get_session)):
    ok = await BanquetService.delete_table(table_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Table not found"
        )
    return None


@BanquetRouter.get("/seat/", response_model=List[BanquetSeatRead])
async def list_seats(
    tableId: str | None = None, session: AsyncSession = Depends(get_session)
):
    return await BanquetService.list_seats(tableId, session)


@BanquetRouter.get("/seat/{seat_id}", response_model=BanquetSeatRead)
async def get_seat(seat_id: int, session: AsyncSession = Depends(get_session)):
    s = await BanquetService.get_seat(seat_id, session)
    if not s:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found"
        )
    return s
