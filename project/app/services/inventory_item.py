from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.inventory_item import InventoryItem, InventoryItemCreate, InventoryItemUpdate


class InventoryItemService:
    @staticmethod
    async def list_inventory_items(session: AsyncSession) -> List[InventoryItem]:
        res = await session.exec(select(InventoryItem))
        return res.all()

    @staticmethod
    async def create_inventory_item(
        inventory_item_in: InventoryItemCreate, session: AsyncSession
    ) -> InventoryItem:
        st = InventoryItem(**inventory_item_in.dict())
        session.add(st)
        await session.commit()
        await session.refresh(st)
        return st

    @staticmethod
    async def get_inventory_item(
        inventory_item_id: str, session: AsyncSession
    ) -> Optional[InventoryItem]:
        res = await session.exec(
            select(InventoryItem).where(InventoryItem.id == inventory_item_id)
        )
        return res.first()

    @staticmethod
    async def update_inventory_item(
        inventory_item_id: str, inventory_item_in: InventoryItemUpdate, session: AsyncSession
    ) -> Optional[InventoryItem]:
        res = await session.exec(
            select(InventoryItem).where(InventoryItem.id == inventory_item_id)
        )
        st = res.first()
        if not st:
            return None
        data = inventory_item_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(st, key, value)
        session.add(st)
        await session.commit()
        await session.refresh(st)
        return st

    @staticmethod
    async def delete_inventory_item(inventory_item_id: str, session: AsyncSession) -> bool:
        res = await session.exec(
            select(InventoryItem).where(InventoryItem.id == inventory_item_id)
        )
        st = res.first()
        if not st:
            return False
        await session.delete(st)
        await session.commit()
        return True
