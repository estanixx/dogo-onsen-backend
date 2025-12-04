from typing import List, Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func

from app.models import (
    Item,
    ItemCreate,
    ItemUpdate,
    ItemIntake,
    Service,
    InventoryOrder,
    Reservation,
    ItemRead,
)


class ItemService:
    @staticmethod
    async def list_items(session: AsyncSession) -> List[Item]:
        res = await session.exec(
                select(Item).options(
                    selectinload(Item.inventory_orders),
                    selectinload(Item.intakes).selectinload(ItemIntake.service).selectinload(Service.reservations),
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
                    selectinload(Item.intakes).selectinload(ItemIntake.service).selectinload(Service.reservations),
                )
        )
        return res.first()

    @staticmethod
    async def list_items_with_quantity(session: AsyncSession) -> List[ItemRead]:
        """
        Return ItemRead list with computed `quantity` using DB-side aggregations to
        avoid triggering lazy loads during serialization.
        """
        # load base items
        items_res = await session.exec(select(Item))
        items = items_res.all()

        # Sum redeemed inventory orders per item
        inv_q = await session.exec(
            select(InventoryOrder.idItem, func.coalesce(func.sum(InventoryOrder.quantity), 0))
            .where(InventoryOrder.redeemed == True)
            .group_by(InventoryOrder.idItem)
        )
        inv_map = {row[0]: int(row[1]) for row in inv_q.all()}

        # Count reservations per service
        res_q = await session.exec(
            select(Reservation.serviceId, func.count(Reservation.id)).group_by(Reservation.serviceId)
        )
        res_map = {row[0]: int(row[1]) for row in res_q.all()}

        # Get intakes for all items
        int_q = await session.exec(select(ItemIntake.itemId, ItemIntake.serviceId, ItemIntake.quantity))
        intakes = int_q.all()

        # Compute consumed per item
        consumed_map: dict[int, int] = {}
        for itemId, serviceId, qty in intakes:
            if serviceId:
                num_res = res_map.get(serviceId, 0)
                consumed_map[itemId] = consumed_map.get(itemId, 0) + (qty * num_res)
            else:
                consumed_map[itemId] = consumed_map.get(itemId, 0) + qty

        # Build ItemRead list
        result: List[ItemRead] = []
        for itm in items:
            ordered = inv_map.get(itm.id, 0)
            consumed = consumed_map.get(itm.id, 0)
            q = ordered - consumed
            result.append(ItemRead(id=itm.id, name=itm.name, image=itm.image, unit=itm.unit, quantity=q))

        return result

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
