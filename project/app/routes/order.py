from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Order, OrderCreate, OrderUpdate
from app.services import OrderService

OrderRouter = APIRouter()


@OrderRouter.get("/", response_model=list[Order])
async def list_orders(session: AsyncSession = Depends(get_session)):
    return await OrderService.list_orders(session)


@OrderRouter.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, session: AsyncSession = Depends(get_session)):
    return await OrderService.create_order(order, session)


@OrderRouter.get("/{order_id}", response_model=Order)
async def get_order(order_id: int, session: AsyncSession = Depends(get_session)):
    o = await OrderService.get_order(order_id, session)
    if not o:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return o


@OrderRouter.put("/{order_id}", response_model=Order)
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
