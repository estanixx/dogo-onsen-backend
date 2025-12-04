from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Item, ItemCreate, ItemUpdate, ItemRead
from app.services import ItemService

ItemRouter = APIRouter()


@ItemRouter.get("/", response_model=list[ItemRead])
async def list_items(session: AsyncSession = Depends(get_session)):
    return await ItemService.list_items(session)


@ItemRouter.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, session: AsyncSession = Depends(get_session)):
    return await ItemService.create_item(item, session)


@ItemRouter.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int, session: AsyncSession = Depends(get_session)):
    itm = await ItemService.get_item(item_id, session)
    if not itm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return itm


@ItemRouter.put("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: int, item: ItemUpdate, session: AsyncSession = Depends(get_session)
):
    itm = await ItemService.update_item(item_id, item, session)
    if not itm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return itm


@ItemRouter.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, session: AsyncSession = Depends(get_session)):
    ok = await ItemService.delete_item(item_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return None
