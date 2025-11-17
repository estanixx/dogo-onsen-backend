from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import (
    BanquetTable,
    BanquetTableCreate,
    BanquetTableUpdate,
    BanquetSeat,
    BanquetSeatCreate,
    BanquetSeatUpdate,
)

BanquetRouter = APIRouter()


@BanquetRouter.get("/table/", response_model=list[BanquetTable])
async def list_tables(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BanquetTable))
    tables = result.scalars().all()
    for t in tables:
        await session.refresh(t, attribute_names=["availableSeats"])
    return tables


@BanquetRouter.post("/table/", response_model=BanquetTable, status_code=status.HTTP_201_CREATED)
async def create_table(table: BanquetTableCreate, session: AsyncSession = Depends(get_session)):
    t = BanquetTable(**table.dict())
    session.add(t)
    # commit to get the table id (UUID)
    await session.commit()
    await session.refresh(t)

    # Auto-create seats for the table according to its capacity
    seats = []
    try:
        cap = int(t.capacity) if t.capacity and t.capacity > 0 else 0
    except Exception:
        cap = 0

    for i in range(1, cap + 1):
        s = BanquetSeat(tableId=t.id, seatNumber=i)
        session.add(s)
        seats.append(s)

    if seats:
        await session.commit()
        # refresh created seats and the table to populate relationships
        for s in seats:
            await session.refresh(s)
        await session.refresh(t)

    return t


@BanquetRouter.get("/table/{table_id}", response_model=BanquetTable)
async def get_table(table_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BanquetTable).where(BanquetTable.id == table_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return t


@BanquetRouter.put("/table/{table_id}", response_model=BanquetTable)
async def update_table(table_id: str, table: BanquetTableUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BanquetTable).where(BanquetTable.id == table_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    data = table.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(t, key, value)

    session.add(t)
    await session.commit()
    await session.refresh(t)
    return t


@BanquetRouter.delete("/table/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(table_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BanquetTable).where(BanquetTable.id == table_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    await session.delete(t)
    await session.commit()
    return None


@BanquetRouter.get("/seat/", response_model=list[BanquetSeat])
async def list_seats(tableId: str | None = None, session: AsyncSession = Depends(get_session)):
    q = select(BanquetSeat)
    if tableId:
        q = q.where(BanquetSeat.tableId == tableId)
    result = await session.execute(q)
    seats = result.scalars().all()
    return seats



@BanquetRouter.get("/seat/{seat_id}", response_model=BanquetSeat)
async def get_seat(seat_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BanquetSeat).where(BanquetSeat.id == seat_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found")
    return s


