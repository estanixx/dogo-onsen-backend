from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Order, OrderCreate, OrderUpdate


class OrderService:
    @staticmethod
    async def list_orders(session: AsyncSession) -> List[Order]:
        # Return only orders where current time is between orderDate and deliveryDate
        now = datetime.now(timezone.utc)
        res = await session.exec(
            select(Order).where(Order.orderDate <= now, Order.deliveryDate >= now)
        )
        return res.all()

    @staticmethod
    async def create_order(order_in: OrderCreate, session: AsyncSession) -> Order:
        # Normalize orderDate to today at 00:00 and deliveryDate to tomorrow at 23:59 (UTC)
        now = datetime.now(timezone.utc)
        start_of_day = datetime(year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc)
        tomorrow = start_of_day + timedelta(days=1)
        delivery_end = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=23, minute=59, tzinfo=timezone.utc)

        # Create order and override dates to normalized values
        order_data = order_in.dict()
        order_data["orderDate"] = start_of_day
        order_data["deliveryDate"] = delivery_end

        order = Order(**order_data)
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

    @staticmethod
    async def get_order(order_id: str, session: AsyncSession) -> Optional[Order]:
        res = await session.exec(select(Order).where(Order.id == order_id))
        return res.first()

    @staticmethod
    async def update_order(
        order_id: str, order_in: OrderUpdate, session: AsyncSession
    ) -> Optional[Order]:
        res = await session.exec(select(Order).where(Order.id == order_id))
        order = res.first()
        if not order:
            return None
        data = order_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(order, key, value)
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

    @staticmethod
    async def delete_order(order_id: str, session: AsyncSession) -> bool:
        res = await session.exec(select(Order).where(Order.id == order_id))
        order = res.first()
        if not order:
            return False
        await session.delete(order)
        await session.commit()
        return True
