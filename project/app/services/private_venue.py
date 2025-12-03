from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import PrivateVenue, PrivateVenueCreate, VenueAccount
from sqlalchemy import exists
from datetime import datetime, timezone


class PrivateVenueService:
    @staticmethod
    async def list_private_venues(filters: Optional[dict], session: AsyncSession):
        if filters and filters.get("startTime") and filters.get("endTime"):
            start_dt = datetime.fromisoformat(filters["startTime"])
            end_dt = datetime.fromisoformat(filters["endTime"])

            overlap_exists = (
                select(VenueAccount.id)
                .where(
                    (VenueAccount.privateVenueId == PrivateVenue.id)
                    & (VenueAccount.startTime <= end_dt)
                    & (VenueAccount.endTime >= start_dt)
                )
                .exists()
            )

            q = select(PrivateVenue).where(~overlap_exists)
            res = await session.exec(q)
            return res.all()

        # fallback
        res = await session.exec(select(PrivateVenue))
        return res.all()

    @staticmethod
    async def today_occupancy_rate(session: AsyncSession) -> float:
        # Calculate percentage of private venues currently occupied
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        res = await session.exec(select(PrivateVenue))
        pvs = res.all()
        if not pvs:
            return 0.0

        total = len(pvs)
        occ_q = select(VenueAccount).where(
            VenueAccount.startTime <= now, VenueAccount.endTime >= now
        )
        occ_res = await session.exec(occ_q)
        occ = occ_res.all()
        # Count unique privateVenueIds
        occ_ids = {a.privateVenueId for a in occ}
        rate = (len(occ_ids) / total) * 100.0
        return rate

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
