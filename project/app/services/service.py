from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Service, ServiceCreate, ServiceUpdate


class ServiceService:
    @staticmethod
    async def list_services(session: AsyncSession) -> List[Service]:
        res = await session.exec(select(Service))
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
