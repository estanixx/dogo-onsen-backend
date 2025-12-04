from typing import List, Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime

from app.models.spirit import Spirit, SpiritCreate, SpiritUpdate, SpiritRead
from app.models import VenueAccount


class SpiritService:
    @staticmethod
    async def list_spirits(session: AsyncSession) -> List[SpiritRead]:
        res = await session.exec(select(Spirit).options(selectinload(Spirit.type)))
        spirits = res.all()

        # Compute which spirits currently have an active VenueAccount (start <= now <= end)
        now = datetime.now()
        q = (
            select(VenueAccount.spiritId)
            .where(VenueAccount.startTime <= now, VenueAccount.endTime >= now)
            .distinct()
        )
        active_res = await session.exec(q)
        active_ids = set(active_res.all() or [])

        out: List[SpiritRead] = []
        for s in spirits:
            read = SpiritRead.from_orm(s)
            read.currentlyInVenue = s.id in active_ids
            out.append(read)
        return out

    @staticmethod
    async def create_spirit(spirit_in: SpiritCreate, session: AsyncSession) -> SpiritRead:
        s = Spirit(**spirit_in.dict())
        session.add(s)
        await session.commit()
        await session.refresh(s)
        # await session.refresh(s.type)
        return await SpiritService.get_spirit(spirit_in.id, session)

    @staticmethod
    async def get_spirit(spirit_id: int, session: AsyncSession) -> Optional[SpiritRead]:
        res = await session.exec(
            select(Spirit)
            .where(Spirit.id == spirit_id)
            .options(selectinload(Spirit.type))
        )
        s = res.first()
        if not s:
            return None

        # Check if this spirit currently has an active venue account
        now = datetime.now()
        overlap_q = select(VenueAccount).where(
            VenueAccount.spiritId == s.id,
            VenueAccount.startTime <= now,
            VenueAccount.endTime >= now,
        )
        overlap_res = await session.exec(overlap_q)
        read = SpiritRead.from_orm(s)
        read.currentlyInVenue = True if overlap_res.first() else False
        return read

    @staticmethod
    async def update_spirit(
        spirit_id: int, spirit_in: SpiritUpdate, session: AsyncSession
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
    async def delete_spirit(spirit_id: int, session: AsyncSession) -> bool:
        res = await session.exec(select(Spirit).where(Spirit.id == spirit_id))
        s = res.first()
        if not s:
            return False
        await session.delete(s)
        await session.commit()
        return True
