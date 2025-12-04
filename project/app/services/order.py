from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Order, OrderCreate, OrderUpdate, InventoryOrder, InventoryOrderCreate


class OrderService:
    @staticmethod
    async def list_orders(session: AsyncSession) -> List[Order]:
        # Return only orders where current time is between orderDate and deliveryDate
        now = datetime.now(timezone.utc)
        stmt = (
            select(Order)
            .where(Order.orderDate <= now, Order.deliveryDate >= now)
            .options(selectinload(Order.items))
        )
        res = await session.exec(stmt)
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
    async def create_order_with_items(
        order_in: OrderCreate,
        items: list[InventoryOrderCreate],
        session: AsyncSession,
    ) -> Order:
        # GMT-5 timezone offset
        gmt_minus_5 = timezone(timedelta(hours=-5))
        now = datetime.now(gmt_minus_5)
        tomorrow = now + timedelta(days=1)
        delivery_end = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=23, minute=59, tzinfo=gmt_minus_5)

        order_data = order_in.dict()
        # Keep orderDate as provided (creation time), only normalize deliveryDate
        order_data["deliveryDate"] = delivery_end

        order = Order(**order_data)
        session.add(order)
        await session.flush()  # get order.id without full commit

        for it in items:
            line = InventoryOrder(idOrder=order.id, idItem=it.idItem, quantity=it.quantity)
            session.add(line)

        await session.commit()
        # Reload order with eager-loaded items in one query
        res = await session.exec(
            select(Order)
            .where(Order.id == order.id)
            .options(selectinload(Order.items))
        )
        return res.first() or order

    @staticmethod
    async def get_order(order_id: int, session: AsyncSession) -> Optional[Order]:
        res = await session.exec(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
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
        for key, value in data.items():
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

    @staticmethod
    async def redeem_order(order_id: int, session: AsyncSession) -> Optional[Order]:
        """Mark all inventory orders for this order as redeemed."""
        res = await session.exec(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        order = res.first()
        if not order:
            return None
        
        # Update all inventory orders to redeemed=True
        for item in order.items:
            item.redeemed = True
            session.add(item)
        
        await session.commit()
        await session.refresh(order)
        return order
