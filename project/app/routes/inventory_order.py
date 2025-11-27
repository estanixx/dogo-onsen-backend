from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import InventoryOrder, InventoryOrderCreate, InventoryOrderUpdate
from app.services import InventoryOrderService

InventoryOrderRouter = APIRouter()


@InventoryOrderRouter.get("/", response_model=list[InventoryOrder])
async def list_inventory_orders(session: AsyncSession = Depends(get_session)):
    return await InventoryOrderService.list_inventory_orders(session)


@InventoryOrderRouter.post(
    "/", response_model=InventoryOrder, status_code=status.HTTP_201_CREATED
)
async def create_inventory_order(
    inventory_order: InventoryOrderCreate, session: AsyncSession = Depends(get_session)
):
    return await InventoryOrderService.create_inventory_order(inventory_order, session)


@InventoryOrderRouter.get("/{inventory_order_id}", response_model=InventoryOrder)
async def get_inventory_order(
    inventory_order_id: str, session: AsyncSession = Depends(get_session)
):
    ii = await InventoryOrderService.get_inventory_order(inventory_order_id, session)
    if not ii:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found"
        )
    return ii


@InventoryOrderRouter.put("/{inventory_order_id}", response_model=InventoryOrder)
async def update_inventory_order(
    inventory_order_id: str,
    inventory_order: InventoryOrderUpdate,
    session: AsyncSession = Depends(get_session),
):
    d = await InventoryOrderService.update_inventory_order(
        inventory_order_id, inventory_order, session
    )
    if not d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found"
        )
    return d


@InventoryOrderRouter.delete("/{inventory_order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_order(
    inventory_order_id: str, session: AsyncSession = Depends(get_session)
):
    ok = await InventoryOrderService.delete_inventory_order(inventory_order_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found"
        )
    return None