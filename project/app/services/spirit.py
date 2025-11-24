from typing import List, Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.spirit import Spirit, SpiritCreate, SpiritUpdate, SpiritRead


class SpiritService:
    @staticmethod
    async def list_spirits(session: AsyncSession) -> List[SpiritRead]:
        res = await session.exec(select(Spirit).options(selectinload(Spirit.type)))
        return res.all()

    @staticmethod
    async def create_spirit(spirit_in: SpiritCreate, session: AsyncSession) -> Spirit:
        s = Spirit(**spirit_in.dict())
        session.add(s)
        await session.commit()
        await session.refresh(s)
        return s

    @staticmethod
    async def get_spirit(spirit_id: str, session: AsyncSession) -> Optional[Spirit]:
        res = await session.exec(select(Spirit).where(Spirit.id == spirit_id))
        return res.first()

    @staticmethod
    async def update_spirit(
        spirit_id: str, spirit_in: SpiritUpdate, session: AsyncSession
    ) -> Optional[Spirit]:
        res = await session.exec(select(Spirit).where(Spirit.id == spirit_id))
        s = res.first()
        if not s:
            return None
        data = spirit_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(s, key, value)
        session.add(s)
        await session.commit()
        await session.refresh(s)
        return s

    @staticmethod
    async def delete_spirit(spirit_id: str, session: AsyncSession) -> bool:
        res = await session.exec(select(Spirit).where(Spirit.id == spirit_id))
        s = res.first()
        if not s:
            return False
        await session.delete(s)
        await session.commit()
        return True
