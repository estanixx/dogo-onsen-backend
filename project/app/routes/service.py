from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Service, ServiceCreate, ServiceUpdate
from app.services import ServiceService

ServiceRouter = APIRouter()


@ServiceRouter.get("/", response_model=list[Service])
async def list_services(session: AsyncSession = Depends(get_session)):
    return await ServiceService.list_services(session)


@ServiceRouter.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate, session: AsyncSession = Depends(get_session)
):
    return await ServiceService.create_service(service, session)


@ServiceRouter.get("/{service_id}", response_model=Service)
async def get_service(service_id: str, session: AsyncSession = Depends(get_session)):
    svc = await ServiceService.get_service(service_id, session)
    if not svc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return svc


@ServiceRouter.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: str,
    service: ServiceUpdate,
    session: AsyncSession = Depends(get_session),
):
    svc = await ServiceService.update_service(service_id, service, session)
    if not svc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return svc


@ServiceRouter.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: str, session: AsyncSession = Depends(get_session)):
    ok = await ServiceService.delete_service(service_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return None
