from typing import List, Optional
from datetime import datetime, date, time, timedelta, timezone
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Reservation, ReservationCreate, ReservationUpdate
from app.models import DateRequest


class ReservationService:
    @staticmethod
    async def list_reservations(
        filters: Optional[dict], session: AsyncSession
    ) -> List[Reservation]:
        q = select(Reservation)
        if filters:
            if (
                "accountId" in filters
                and filters["accountId"] is not None
                and filters["accountId"] != ""
            ):
                q = q.where(Reservation.accountId == filters["accountId"])
            if (
                "serviceId" in filters
                and filters["serviceId"] is not None
                and filters["serviceId"] != ""
            ):
                q = q.where(Reservation.serviceId == filters["serviceId"])
            if (
                "datetime" in filters
                and filters["datetime"] is not None
                and filters["datetime"] != ""
            ):
                # `datetime` filter may be a date (YYYY-MM-DD) or a full ISO datetime.
                # - If it's a date, return reservations whose startTime falls within that UTC date.
                # - If it's a full datetime, return reservations whose startTime equals that datetime.
                val = filters["datetime"]
                try:
                    if isinstance(val, str):
                        if len(val) <= 10 and "-" in val:
                            # date string
                            d = date.fromisoformat(val)
                            start_dt = datetime.combine(d, time.min).replace(
                                tzinfo=timezone.utc
                            )
                            end_dt = start_dt + timedelta(days=1)
                            q = q.where(Reservation.startTime >= start_dt).where(
                                Reservation.startTime < end_dt
                            )
                        else:
                            # full ISO datetime string
                            dt = datetime.fromisoformat(val)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            q = q.where(Reservation.startTime == dt)
                    elif isinstance(val, datetime):
                        dt = val
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        q = q.where(Reservation.startTime == dt)
                    elif isinstance(val, date):
                        d = val
                        start_dt = datetime.combine(d, time.min).replace(
                            tzinfo=timezone.utc
                        )
                        end_dt = start_dt + timedelta(days=1)
                        q = q.where(Reservation.startTime >= start_dt).where(
                            Reservation.startTime < end_dt
                        )
                    else:
                        # unknown type; ignore the filter
                        pass
                except Exception:
                    raise ValueError("Invalid datetime filter format")

        res = await session.exec(q)
        return res.all()

    @staticmethod
    async def create_reservation(
        reservation_in: ReservationCreate, session: AsyncSession
    ) -> Reservation:
        r = Reservation(**reservation_in.dict())
        session.add(r)
        await session.commit()
        await session.refresh(r)
        return r

    @staticmethod
    async def get_banquet_reservations_for_date(
        payload: DateRequest, session: AsyncSession
    ) -> List[Reservation]:
        # parse date (accept YYYY-MM-DD or full ISO datetime)
        try:
            if len(payload.date) <= 10 and "-" in payload.date:
                d = date.fromisoformat(payload.date)
            else:
                d = datetime.fromisoformat(payload.date).date()
        except Exception:
            raise ValueError("Invalid date format")

        start_dt = datetime.combine(d, time.min).replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(days=1)

        q = (
            select(Reservation)
            .where(Reservation.seatId != None)
            .where(Reservation.startTime >= start_dt)
            .where(Reservation.startTime < end_dt)
        )
        res = await session.exec(q)
        return res.all()

    @staticmethod
    async def get_reservation(
        reservation_id: str, session: AsyncSession
    ) -> Optional[Reservation]:
        res = await session.exec(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        return res.first()

    @staticmethod
    async def update_reservation(
        reservation_id: str, reservation_in: ReservationUpdate, session: AsyncSession
    ) -> Optional[Reservation]:
        res = await session.exec(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        r = res.first()
        if not r:
            return None
        data = reservation_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(r, key, value)
        session.add(r)
        await session.commit()
        await session.refresh(r)
        return r

    @staticmethod
    async def delete_reservation(reservation_id: str, session: AsyncSession) -> bool:
        res = await session.exec(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        r = res.first()
        if not r:
            return False
        await session.delete(r)
        await session.commit()
        return True
