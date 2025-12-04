from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Spirit, SpiritCreate, SpiritUpdate, SpiritRead
from app.services import SpiritService

SpiritRouter = APIRouter()


@SpiritRouter.get("/", response_model=list[SpiritRead])
async def list_spirits(session: AsyncSession = Depends(get_session)):
    return await SpiritService.list_spirits(session)


@SpiritRouter.post("/", response_model=SpiritRead, status_code=status.HTTP_201_CREATED)
async def create_spirit(
    spirit: SpiritCreate, session: AsyncSession = Depends(get_session)
):
    return await SpiritService.create_spirit(spirit, session)


@SpiritRouter.get("/{spirit_id}", response_model=SpiritRead)
async def get_spirit(spirit_id: int, session: AsyncSession = Depends(get_session)):
    s = await SpiritService.get_spirit(spirit_id, session)
    if not s:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spirit not found"
        )
    return s


@SpiritRouter.put("/{spirit_id}", response_model=Spirit)
async def update_spirit(
    spirit_id: int, spirit: SpiritUpdate, session: AsyncSession = Depends(get_session)
):
    s = await SpiritService.update_spirit(spirit_id, spirit, session)
    if not s:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spirit not found"
        )
    return s


@SpiritRouter.delete("/{spirit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spirit(spirit_id: int, session: AsyncSession = Depends(get_session)):
    ok = await SpiritService.delete_spirit(spirit_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spirit not found"
        )
    return None
