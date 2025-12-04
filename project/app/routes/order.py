from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Order, OrderCreate, OrderUpdate, InventoryOrderCreate, OrderRead
from app.services import OrderService

OrderRouter = APIRouter()


@OrderRouter.get("/", response_model=list[OrderRead])
async def list_orders(session: AsyncSession = Depends(get_session)):
    return await OrderService.list_orders(session)


@OrderRouter.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, session: AsyncSession = Depends(get_session)):
    return await OrderService.create_order(order, session)


@OrderRouter.post("/with_items", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order_with_items(
    payload: dict,
    session: AsyncSession = Depends(get_session),
):
    try:
        order = OrderCreate(**payload.get("order", {}))
        # items may omit idOrder; we validate required fields manually
        items_raw = payload.get("items", [])
        items_in = [InventoryOrderCreate(idItem=it["idItem"], quantity=it["quantity"]) for it in items_raw]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return await OrderService.create_order_with_items(order, items_in, session)


@OrderRouter.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    o = await OrderService.get_order(order_id, session)
    if not o:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return o


@OrderRouter.put("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: int, order: OrderUpdate, session: AsyncSession = Depends(get_session)
):
    o = await OrderService.update_order(order_id, order, session)
    if not o:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return o


@OrderRouter.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, session: AsyncSession = Depends(get_session)):
    ok = await OrderService.delete_order(order_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return None


@OrderRouter.put("/{order_id}/redeem", response_model=OrderRead)
async def redeem_order(order_id: int, session: AsyncSession = Depends(get_session)):
    """Mark all inventory orders for this order as redeemed."""
    order = await OrderService.redeem_order(order_id, session)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order
