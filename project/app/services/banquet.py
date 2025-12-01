from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta, timezone
from app.core.constants import TIME_SLOTS
from sqlmodel import select
from sqlalchemy.orm import selectinload

from app.services.spirit import SpiritService
from app.services.type_relation import TypeRelationService
from app.models import BanquetTable, BanquetSeat, Reservation, VenueAccount, Spirit
from sqlalchemy import func, exists
from app.core.tools import logger


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
        spirit = await SpiritService.get_spirit(spirit_id, session)
        if not spirit:
            return []

        typeId = spirit.typeId
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

            def _map_seats(seat):
                seat_d = seat.dict()
                resv = reservations_map.get(seat.id)
                if resv:
                    seat_d["reservationId"] = resv.id
                    seat_d["available"] = False
                    seat_d["spirit"] = (
                        getattr(resv.account, "spirit", None).dict()
                        if getattr(resv.account, "spirit", None)
                        else None
                    )
                    seat_d["spirit"]["type"] = (
                        getattr(resv.account.spirit, "type", None).dict()
                        if getattr(resv.account.spirit, "type", None)
                        else None
                    )

                return seat_d

        out_tables = []
        for t in tables:
            # Go through each table
            tbl = t.dict()
            occupies = []

            seats_out = list(
                map(
                    _map_seats,
                    sorted(
                        getattr(t, "availableSeats", []).copy(),
                        key=lambda s: s.seatNumber,
                    ),
                )
            )
            for i, seat_d in enumerate(seats_out):
                nextSeat = seats_out[i + 1] if i + 1 < len(seats_out) else seats_out[0]
                pastSeat = seats_out[i - 1] if i - 1 >= 0 else seats_out[-1]
                # Go through each seat
                if seat_d.get("spirit", None):
                    sp = seat_d["spirit"]
                    tr = await TypeRelationService.get_relation_between(
                        typeId, sp["typeId"], session
                    )
                    relation = tr.relation if tr else "allow"
                    if relation == "forbidden":
                        tbl["available"] = False
                    elif relation == "separation":
                        pastSeat["available"] = False
                        nextSeat["available"] = False
                    occupies.append(sp)
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

        # Timeslot strings are expressed in Bogota local time (UTC-5).
        BOGOTA_TZ = timezone(timedelta(hours=-5))

        # Compare the requested day against "today" in Bogota.
        today_bogota = datetime.now(timezone.utc).astimezone(BOGOTA_TZ).date()
        if d < today_bogota:
            return []

        # If the requested date is today in Bogota, compute current UTC time to
        # exclude timeslots that have already passed when converted to UTC.
        is_today = d == today_bogota
        now_utc = datetime.now(timezone.utc) if is_today else None

        # For each timeslot, ask `list_available_seats` for the slot start time
        # and treat a slot as available if any seat across all tables is free.
        available_slots: List[str] = []

        for slot in TIME_SLOTS:
            # parse slot like '09:00 AM'
            try:
                slot_time = datetime.strptime(slot, "%I:%M %p").time()
            except Exception:
                continue
            # Interpret the slot time as Bogota-local, then convert to UTC
            # for comparisons and for passing into the seat-availability
            # routine which expects UTC datetimes.
            slot_start_local = datetime.combine(d, slot_time).replace(tzinfo=BOGOTA_TZ)
            slot_start = slot_start_local.astimezone(timezone.utc)
            slot_end = slot_start + timedelta(hours=1)

            # If we're computing for today (Bogota), skip slots that have already passed.
            if is_today and now_utc is not None and slot_end <= now_utc:
                continue

            # Use the existing seat-availability logic which applies type
            # restrictions and reservation checks per seat. Pass UTC datetime.
            try:
                tables = await BanquetService.list_available_seats(
                    spirit_id, slot_start, session
                )
            except Exception:
                # If something goes wrong computing seats for this slot, skip it.
                continue

            slot_has_free = False
            for tbl in tables:
                # If the table itself is marked unavailable, treat all seats as unavailable
                table_unavailable = tbl.get("available") is False

                seats = tbl.get("availableSeats", [])
                for seat in seats:
                    if table_unavailable:
                        # table-level restriction => seat unavailable
                        continue

                    # If seat has a reservationId it's taken. If 'available' is present
                    # and False then it's restricted/unavailable.
                    if seat.get("reservationId"):
                        continue

                    if seat.get("available") is False:
                        continue

                    # Seat is free for this slot
                    slot_has_free = True
                    break

                if slot_has_free:
                    break

            if slot_has_free:
                available_slots.append(slot)

        return available_slots
