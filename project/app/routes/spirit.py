from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.spirit import Spirit, SpiritCreate, SpiritUpdate

SpiritRouter = APIRouter()


@SpiritRouter.get("/", response_model=list[Spirit])
async def list_spirits(session: AsyncSession = Depends(get_session)):
    q = select(Spirit)
    result = await session.execute(q)
    return result.scalars().all()


@SpiritRouter.post("/", response_model=Spirit, status_code=status.HTTP_201_CREATED)
async def create_spirit(spirit: SpiritCreate, session: AsyncSession = Depends(get_session)):
    s = Spirit(**spirit.dict())
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return s


@SpiritRouter.get("/{spirit_id}", response_model=Spirit)
async def get_spirit(spirit_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Spirit).where(Spirit.id == spirit_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spirit not found")
    return s


@SpiritRouter.put("/{spirit_id}", response_model=Spirit)
async def update_spirit(spirit_id: str, spirit: SpiritUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Spirit).where(Spirit.id == spirit_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spirit not found")
    
    data = spirit.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(s, key, value)

    session.add(s)
    await session.commit()
    await session.refresh(s)
    return s


@SpiritRouter.delete("/{spirit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spirit(spirit_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Spirit).where(Spirit.id == spirit_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spirit not found")

    await session.delete(s)
    await session.commit()
    return None