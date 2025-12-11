from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, date, time, timedelta, timezone
from sqlalchemy.orm import selectinload
from app.core.constants import TIME_SLOTS

from app.models.service import Service as ServiceModel, ServiceCreate, ServiceUpdate

# keep the original name for type hints and instantiation
Service = ServiceModel
from app.models.reservation import Reservation, ReservationRead
from app.models.utils import ServiceSummary, ServiceWithReservations


class ServiceService:
    @staticmethod
    async def list_services(
        session: AsyncSession, q: Optional[str] = None
    ) -> List[Service]:
        res = await session.exec(
            select(Service).where(Service.name.contains(q)) if q else select(Service)
        )
        return res.all()

    @staticmethod
    async def create_service(
        service_in: ServiceCreate, session: AsyncSession
    ) -> Service:
        svc = Service(**service_in.dict())
        session.add(svc)
        await session.commit()
        await session.refresh(svc)
        return svc

    @staticmethod
    async def get_service(service_id: str, session: AsyncSession) -> Optional[Service]:
        res = await session.exec(select(Service).where(Service.id == service_id))
        return res.first()

    @staticmethod
    async def update_service(
        service_id: str, service_in: ServiceUpdate, session: AsyncSession
    ) -> Optional[Service]:
        res = await session.exec(select(Service).where(Service.id == service_id))
        svc = res.first()
        if not svc:
            return None
        data = service_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(svc, key, value)
        session.add(svc)
        await session.commit()
        await session.refresh(svc)
        return svc

    @staticmethod
    async def delete_service(service_id: str, session: AsyncSession) -> bool:
        res = await session.exec(select(Service).where(Service.id == service_id))
        svc = res.first()
        if not svc:
            return False
        await session.delete(svc)
        await session.commit()
        return True

    @staticmethod
    async def get_available_time_slots(
        service_id: str, date_payload: str, session: AsyncSession
    ) -> List[str]:
        """Return TIME_SLOTS that are not in the past and not reserved for the service on the date."""
        try:
            if len(date_payload) <= 10 and "-" in date_payload:
                d = date.fromisoformat(date_payload)
            else:
                d = datetime.fromisoformat(date_payload).date()
        except Exception:
            raise ValueError("Invalid date format")

        bogota_tz = timezone(timedelta(hours=-5))
        today_bogota = datetime.now(timezone.utc).astimezone(bogota_tz).date()
        if d < today_bogota:
            return []

        is_today = d == today_bogota
        now_utc = datetime.now(timezone.utc) if is_today else None

        start_dt = datetime.combine(d, time.min).replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(days=1)

        q = (
            select(Reservation)
            .where(Reservation.serviceId == service_id)
            .where(Reservation.startTime >= start_dt)
            .where(Reservation.startTime < end_dt)
        )
        res = await session.exec(q)
        reservations = res.all()

        available: List[str] = []

        for slot in TIME_SLOTS:
            try:
                slot_time = datetime.strptime(slot, "%I:%M %p").time()
            except Exception:
                continue

            slot_start_local = datetime.combine(d, slot_time).replace(tzinfo=bogota_tz)
            slot_start = slot_start_local.astimezone(timezone.utc)
            slot_end = slot_start + timedelta(hours=1)

            if is_today and now_utc is not None and slot_end <= now_utc:
                continue

            slot_taken = False
            for r in reservations:
                if r.startTime is None:
                    continue
                res_start = r.startTime
                res_end = getattr(r, "endTime", None) or (
                    res_start + timedelta(hours=1)
                )
                if res_start < slot_end and res_end > slot_start:
                    slot_taken = True
                    break

            if not slot_taken:
                available.append(slot)

        return available

    @staticmethod
    async def today_reservations_per_service(
        session: AsyncSession,
    ) -> List[ServiceWithReservations]:
        # Compute today's start/end in UTC
        today = datetime.now(timezone.utc).date()
        start_dt = datetime.combine(today, time.min).replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(days=1)

        # Fetch reservations for today and their services
        q = (
            select(Reservation)
            .where(Reservation.startTime >= start_dt)
            .where(Reservation.startTime < end_dt)
            .options(selectinload(Reservation.service))
        )
        res = await session.exec(q)
        reservations = res.all()

        # Build a mapping serviceId -> list of reservations
        groups: dict[str, list[Reservation]] = {}
        for r in reservations:
            sid = r.serviceId or (
                getattr(r.service, "id", None) if getattr(r, "service", None) else None
            )
            if sid is None:
                continue
            groups.setdefault(sid, []).append(r)

        # Load all services and return a summary per-service (count may be zero)
        svc_q = select(ServiceModel)
        svc_res = await session.exec(svc_q)
        svcs = svc_res.all()

        out: List[ServiceWithReservations] = []
        for svc in svcs:
            rlist = groups.get(svc.id, [])
            svc_summary = ServiceSummary(
                id=svc.id,
                name=svc.name,
                eiltRate=svc.eiltRate,
                image=getattr(svc, "image", None),
                description=getattr(svc, "description", None),
            )
            out.append(
                ServiceWithReservations(
                    service=svc_summary,
                    reservations_count=len(rlist),
                )
            )

        return out
