from typing import List, Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Item, ItemCreate, ItemUpdate


class ItemService:
    @staticmethod
    async def list_items(session: AsyncSession) -> List[Item]:
        res = await session.exec(
            select(Item).options(
                selectinload(Item.inventory_orders),
                selectinload(Item.intakes)
            )
        )
        return res.all()

    @staticmethod
    async def create_item(item_in: ItemCreate, session: AsyncSession) -> Item:
        item = Item(**item_in.dict())
        session.add(item)
        await session.commit()
        await session.refresh(item, ['inventory_orders', 'intakes'])
        return item

    @staticmethod
    async def get_item(item_id: int, session: AsyncSession) -> Optional[Item]:
        res = await session.exec(
            select(Item).where(Item.id == item_id).options(
                selectinload(Item.inventory_orders),
                selectinload(Item.intakes)
            )
        )
        return res.first()

    @staticmethod
    async def update_item(
        item_id: int, item_in: ItemUpdate, session: AsyncSession
    ) -> Optional[Item]:
        res = await session.exec(select(Item).where(Item.id == item_id))
        item = res.first()
        if not item:
            return None
        data = item_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(item, key, value)
        session.add(item)
        await session.commit()
        await session.refresh(item, ['inventory_orders', 'intakes'])
        return item

    @staticmethod
    async def delete_item(item_id: int, session: AsyncSession) -> bool:
        res = await session.exec(select(Item).where(Item.id == item_id))
        item = res.first()
        if not item:
            return False
        await session.delete(item)
        await session.commit()
        return True
