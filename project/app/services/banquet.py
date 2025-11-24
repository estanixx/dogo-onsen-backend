from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta, timezone
from app.core.constants import TIME_SLOTS
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.models import BanquetTable, BanquetSeat, Reservation, VenueAccount, Spirit
from sqlalchemy import func, exists


class BanquetService:
    """Service layer for banquet-related DB operations.

    All methods are async and expect an `AsyncSession` passed from the caller.
    """

    @staticmethod
    async def list_tables(session) -> List[BanquetTable]:
        res = await session.exec(
            select(BanquetTable).options(selectinload(BanquetTable.availableSeats))
        )
        return res.all()

    @staticmethod
    async def list_available_seats(
        spirit_id: str, start_dt: datetime, session
    ) -> List[Dict]:
        # Parse incoming date/datetime and normalize to UTC

        end_dt = start_dt + timedelta(hours=1)

        # Load tables with seats
        res = await session.exec(
            select(BanquetTable).options(selectinload(BanquetTable.availableSeats))
        )
        tables = res.all()

        # Collect seat ids to find overlapping reservations
        seat_ids = [
            s.id
            for t in tables
            for s in getattr(t, "availableSeats", [])
            if s.id is not None
        ]

        reservations_map = {}
        if seat_ids:
            q = (
                select(Reservation)
                .where(
                    Reservation.seatId.in_(seat_ids),
                    Reservation.startTime < end_dt,
                    Reservation.endTime > start_dt,
                )
                .options(
                    selectinload(Reservation.account)
                    .selectinload(VenueAccount.spirit)
                    .selectinload(Spirit.type)
                )
            )
            res2 = await session.exec(q)
            found = res2.all()
            # Map seatId -> first matching reservation
            for r in found:
                if r.seatId not in reservations_map:
                    reservations_map[r.seatId] = r

        out_tables = []
        for t in tables:
            # Go through each table
            tbl = t.dict()
            occupies = []
            seats_out = []
            for s in getattr(t, "availableSeats", []) or []:
                # Go through each seat
                seat_d = s.dict()
                resv = reservations_map.get(s.id)
                if resv:
                    seat_d["reservationId"] = resv.id
                    seat_d["available"] = False
                    acct = getattr(resv, "account", None)
                    if acct and getattr(acct, "spirit", None):
                        sp = acct.spirit
                        sp_d = sp.dict()
                        if getattr(sp, "type", None):
                            sp_d["type"] = sp.type.dict()
                        occupies.append(sp_d)
                seats_out.append(seat_d)
            tbl["availableSeats"] = seats_out
            tbl["occupies"] = occupies
            out_tables.append(tbl)

        return out_tables

    @staticmethod
    async def create_table(table_create, session) -> BanquetTable:
        t = BanquetTable(**table_create.dict())
        session.add(t)
        await session.commit()
        await session.refresh(t)

        # auto-create seats
        seats = []
        try:
            cap = int(t.capacity) if t.capacity and t.capacity > 0 else 0
        except Exception:
            cap = 0
        for i in range(1, cap + 1):
            s = BanquetSeat(tableId=t.id, seatNumber=i)
            session.add(s)
            seats.append(s)
        if seats:
            await session.commit()
            for s in seats:
                await session.refresh(s)

        await session.refresh(t)
        res = await session.exec(
            select(BanquetTable)
            .where(BanquetTable.id == t.id)
            .options(selectinload(BanquetTable.availableSeats))
        )
        return res.first()

    @staticmethod
    async def get_table(table_id: str, session) -> Optional[BanquetTable]:
        res = await session.exec(
            select(BanquetTable)
            .where(BanquetTable.id == table_id)
            .options(selectinload(BanquetTable.availableSeats))
        )
        return res.first()

    @staticmethod
    async def update_table(
        table_id: str, table_update, session
    ) -> Optional[BanquetTable]:
        result = await session.exec(
            select(BanquetTable).where(BanquetTable.id == table_id)
        )
        t = result.first()
        if not t:
            return None
        data = table_update.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(t, key, value)
        session.add(t)
        await session.commit()
        await session.refresh(t)
        return t

    @staticmethod
    async def delete_table(table_id: str, session) -> bool:
        result = await session.exec(
            select(BanquetTable).where(BanquetTable.id == table_id)
        )
        t = result.first()
        if not t:
            return False
        await session.delete(t)
        await session.commit()
        return True

    @staticmethod
    async def list_seats(tableId: Optional[str], session) -> List[BanquetSeat]:
        q = select(BanquetSeat)
        if tableId:
            q = q.where(BanquetSeat.tableId == tableId)
        res = await session.exec(q)
        return res.all()

    @staticmethod
    async def get_seat(seat_id: int, session) -> Optional[BanquetSeat]:
        res = await session.exec(select(BanquetSeat).where(BanquetSeat.id == seat_id))
        return res.first()

    @staticmethod
    async def get_available_time_slots(spirit_id: str, d: date, session) -> List[str]:
        """Return TIME_SLOTS where at least one seat is free for the given spirit on date `d`.

        This fetches tables and all reservations for the day once, then checks each slot
        for any seat without an overlapping reservation.
        """

        # normalize day to UTC midnight
        start_of_day = datetime.combine(d, time.min).replace(tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)

        # For each timeslot, count seats that have no overlapping reservation
        available_slots: List[str] = []

        for slot in TIME_SLOTS:
            # parse slot like '09:00 AM'
            try:
                slot_time = datetime.strptime(slot, "%I:%M %p").time()
            except Exception:
                continue
            slot_start = datetime.combine(d, slot_time).replace(tzinfo=timezone.utc)
            slot_end = slot_start + timedelta(hours=1)

            # Build EXISTS subquery: does a reservation exist for the seat overlapping the slot?
           

            overlap_subq = select(Reservation).where(
                Reservation.seatId == BanquetSeat.id,
                Reservation.startTime < slot_end,
                Reservation.endTime > slot_start,
            )

            # Count seats that do NOT have an overlapping reservation
            count_q = (
                select(func.count())
                .select_from(BanquetSeat)
                .where(~exists(overlap_subq))
            )
            res_count = await session.exec(count_q)
            try:
                free_count = int(res_count.one())
            except Exception:
                # fallback to scalar
                free_count = int(res_count.scalar_one() or 0)

            if free_count > 0:
                available_slots.append(slot)

        return available_slots
