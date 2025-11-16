from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.service import Service, ServiceCreate

ServiceRouter = APIRouter()


@ServiceRouter.get("/", response_model=list[Service])
async def list_services(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Service))
    services = result.scalars().all()
    return services


@ServiceRouter.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(service: ServiceCreate, session: AsyncSession = Depends(get_session)):
    svc = Service(**service.dict())
    session.add(svc)
    await session.commit()
    await session.refresh(svc)
    return svc


@ServiceRouter.get("/{service_id}", response_model=Service)
async def get_service(service_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Service).where(Service.id == service_id))
    svc = result.scalars().first()
    if not svc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return svc


@ServiceRouter.put("/{service_id}", response_model=Service)
async def update_service(service_id: str, service: ServiceCreate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Service).where(Service.id == service_id))
    svc = result.scalars().first()
    if not svc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    svc_data = service.dict()
    for key, value in svc_data.items():
        setattr(svc, key, value)

    session.add(svc)
    await session.commit()
    await session.refresh(svc)
    return svc


@ServiceRouter.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Service).where(Service.id == service_id))
    svc = result.scalars().first()
    if not svc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    await session.delete(svc)
    await session.commit()
    return None