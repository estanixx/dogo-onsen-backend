from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.spirit_type import SpiritType, SpiritTypeCreate, SpiritTypeUpdate

SpiritTypeRouter = APIRouter()


@SpiritTypeRouter.get("/", response_model=list[SpiritType])
async def list_spirit_types(session: AsyncSession = Depends(get_session)):
    q = select(SpiritType)
    result = await session.execute(q)
    return result.scalars().all()


@SpiritTypeRouter.post("/", response_model=SpiritType, status_code=status.HTTP_201_CREATED)
async def create_spirit_type(spirit_type: SpiritTypeCreate, session: AsyncSession = Depends(get_session)):
    st = SpiritType(**spirit_type.dict())
    session.add(st)
    await session.commit()
    await session.refresh(st)
    return st


@SpiritTypeRouter.get("/{spirit_type_id}", response_model=SpiritType)
async def get_spirit_type(spirit_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(SpiritType).where(SpiritType.id == spirit_type_id))
    st = result.scalars().first()
    if not st:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spirit type not found")
    return st


@SpiritTypeRouter.put("/{spirit_type_id}", response_model=SpiritType)
async def update_spirit_type(spirit_type_id: str, spirit_type: SpiritTypeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(SpiritType).where(SpiritType.id == spirit_type_id))
    st = result.scalars().first()
    if not st:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spirit type not found")
    
    data = spirit_type.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(st, key, value)

    session.add(st)
    await session.commit()
    await session.refresh(st)
    return st


@SpiritTypeRouter.delete("/{spirit_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spirit_type(spirit_type_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(SpiritType).where(SpiritType.id == spirit_type_id))
    st = result.scalars().first()
    if not st:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spirit type not found")

    await session.delete(st)
    await session.commit()
    return None