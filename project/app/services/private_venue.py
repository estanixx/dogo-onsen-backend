from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import PrivateVenue, PrivateVenueCreate


class PrivateVenueService:
    @staticmethod
    async def list_private_venues(session: AsyncSession) -> List[PrivateVenue]:
        res = await session.exec(select(PrivateVenue))
        return res.all()

    @staticmethod
    async def create_private_venue(
        pv_in: PrivateVenueCreate, session: AsyncSession
    ) -> PrivateVenue:
        pv = PrivateVenue(**pv_in.dict(exclude_unset=True))
        session.add(pv)
        await session.commit()
        await session.refresh(pv)
        return pv

    @staticmethod
    async def get_private_venue(
        pv_id: int, session: AsyncSession
    ) -> Optional[PrivateVenue]:
        res = await session.exec(select(PrivateVenue).where(PrivateVenue.id == pv_id))
        return res.first()
