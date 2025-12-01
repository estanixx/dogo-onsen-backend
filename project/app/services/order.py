from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Order, OrderCreate, OrderUpdate


class OrderService:
    @staticmethod
    async def list_orders(session: AsyncSession) -> List[Order]:
        res = await session.exec(select(Order))
        return res.all()

    @staticmethod
    async def create_order(order_in: OrderCreate, session: AsyncSession) -> Order:
        order = Order(**order_in.dict())
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

    @staticmethod
    async def get_order(order_id: int, session: AsyncSession) -> Optional[Order]:
        res = await session.exec(select(Order).where(Order.id == order_id))
        return res.first()

    @staticmethod
    async def update_order(
        order_id: int, order_in: OrderUpdate, session: AsyncSession
    ) -> Optional[Order]:
        res = await session.exec(select(Order).where(Order.id == order_id))
        order = res.first()
        if not order:
            return None
        data = order_in.dict(exclude_unset=True)
        for key, value in data.orders():
            setattr(order, key, value)
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

    @staticmethod
    async def delete_order(order_id: int, session: AsyncSession) -> bool:
        res = await session.exec(select(Order).where(Order.id == order_id))
        order = res.first()
        if not order:
            return False
        await session.delete(order)
        await session.commit()
        return True
