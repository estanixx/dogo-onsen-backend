from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.inventory_order import (
    InventoryOrder,
    InventoryOrderCreate,
    InventoryOrderUpdate,
)


class InventoryOrderService:
    @staticmethod
    async def list_inventory_orders(session: AsyncSession) -> List[InventoryOrder]:
        res = await session.exec(select(InventoryOrder))
        return res.all()

    @staticmethod
    async def create_inventory_order(
        inventory_order_in: InventoryOrderCreate, session: AsyncSession
    ) -> InventoryOrder:
        st = InventoryOrder(**inventory_order_in.dict())
        session.add(st)
        await session.commit()
        await session.refresh(st)
        return st

    @staticmethod
    async def get_inventory_order(
        inventory_order_id: str, session: AsyncSession
    ) -> Optional[InventoryOrder]:
        res = await session.exec(
            select(InventoryOrder).where(InventoryOrder.id == inventory_order_id)
        )
        return res.first()

    @staticmethod
    async def update_inventory_order(
        inventory_order_id: str,
        inventory_order_in: InventoryOrderUpdate,
        session: AsyncSession,
    ) -> Optional[InventoryOrder]:
        res = await session.exec(
            select(InventoryOrder).where(InventoryOrder.id == inventory_order_id)
        )
        st = res.first()
        if not st:
            return None
        data = inventory_order_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(st, key, value)
        session.add(st)
        await session.commit()
        await session.refresh(st)
        return st

    @staticmethod
    async def delete_inventory_order(
        inventory_order_id: str, session: AsyncSession
    ) -> bool:
        res = await session.exec(
            select(InventoryOrder).where(InventoryOrder.id == inventory_order_id)
        )
        st = res.first()
        if not st:
            return False
        await session.delete(st)
        await session.commit()
        return True
