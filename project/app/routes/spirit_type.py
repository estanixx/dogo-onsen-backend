from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import SpiritType, SpiritTypeCreate, SpiritTypeUpdate
from app.services import SpiritTypeService

SpiritTypeRouter = APIRouter()


@SpiritTypeRouter.get("/", response_model=list[SpiritType])
async def list_spirit_types(session: AsyncSession = Depends(get_session)):
    return await SpiritTypeService.list_spirit_types(session)


@SpiritTypeRouter.post(
    "/", response_model=SpiritType, status_code=status.HTTP_201_CREATED
)
async def create_spirit_type(
    spirit_type: SpiritTypeCreate, session: AsyncSession = Depends(get_session)
):
    return await SpiritTypeService.create_spirit_type(spirit_type, session)


@SpiritTypeRouter.get("/{spirit_type_id}", response_model=SpiritType)
async def get_spirit_type(
    spirit_type_id: str, session: AsyncSession = Depends(get_session)
):
    st = await SpiritTypeService.get_spirit_type(spirit_type_id, session)
    if not st:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spirit type not found"
        )
    return st


@SpiritTypeRouter.put("/{spirit_type_id}", response_model=SpiritType)
async def update_spirit_type(
    spirit_type_id: str,
    spirit_type: SpiritTypeUpdate,
    session: AsyncSession = Depends(get_session),
):
    st = await SpiritTypeService.update_spirit_type(
        spirit_type_id, spirit_type, session
    )
    if not st:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spirit type not found"
        )
    return st


@SpiritTypeRouter.delete("/{spirit_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spirit_type(
    spirit_type_id: str, session: AsyncSession = Depends(get_session)
):
    ok = await SpiritTypeService.delete_spirit_type(spirit_type_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Spirit type not found"
        )
    return None
