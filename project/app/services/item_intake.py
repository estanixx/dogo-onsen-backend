from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import ItemIntake, ItemIntakeCreate, ItemIntakeUpdate


class ItemIntakeService:
    @staticmethod
    async def list_item_intakes(session: AsyncSession) -> List[ItemIntake]:
        res = await session.exec(select(ItemIntake))
        return res.all()

    @staticmethod
    async def create_item_intake(
        item_intake_in: ItemIntakeCreate, session: AsyncSession
    ) -> ItemIntake:
        intake = ItemIntake(**item_intake_in.dict())
        session.add(intake)
        await session.commit()
        await session.refresh(intake)
        return intake

    @staticmethod
    async def get_item_intake(
        intake_id: int, session: AsyncSession
    ) -> Optional[ItemIntake]:
        res = await session.exec(select(ItemIntake).where(ItemIntake.id == intake_id))
        return res.first()

    @staticmethod
    async def delete_item_intake(intake_id: int, session: AsyncSession) -> bool:
        res = await session.exec(select(ItemIntake).where(ItemIntake.id == intake_id))
        intake = res.first()
        if not intake:
            return False
        await session.delete(intake)
        await session.commit()
        return True
