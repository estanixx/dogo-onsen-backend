from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.spirit_type import SpiritType, SpiritTypeCreate, SpiritTypeUpdate


class SpiritTypeService:
    @staticmethod
    async def list_spirit_types(session: AsyncSession) -> List[SpiritType]:
        res = await session.exec(select(SpiritType))
        return res.all()

    @staticmethod
    async def create_spirit_type(
        spirit_type_in: SpiritTypeCreate, session: AsyncSession
    ) -> SpiritType:
        st = SpiritType(**spirit_type_in.dict())
        session.add(st)
        await session.commit()
        await session.refresh(st)
        return st

    @staticmethod
    async def get_spirit_type(
        spirit_type_id: str, session: AsyncSession
    ) -> Optional[SpiritType]:
        res = await session.exec(
            select(SpiritType).where(SpiritType.id == spirit_type_id)
        )
        return res.first()

    @staticmethod
    async def update_spirit_type(
        spirit_type_id: str, spirit_type_in: SpiritTypeUpdate, session: AsyncSession
    ) -> Optional[SpiritType]:
        res = await session.exec(
            select(SpiritType).where(SpiritType.id == spirit_type_id)
        )
        st = res.first()
        if not st:
            return None
        data = spirit_type_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(st, key, value)
        session.add(st)
        await session.commit()
        await session.refresh(st)
        return st

    @staticmethod
    async def delete_spirit_type(spirit_type_id: str, session: AsyncSession) -> bool:
        res = await session.exec(
            select(SpiritType).where(SpiritType.id == spirit_type_id)
        )
        st = res.first()
        if not st:
            return False
        await session.delete(st)
        await session.commit()
        return True
