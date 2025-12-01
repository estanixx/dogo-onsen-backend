from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import PrivateVenue, PrivateVenueCreate
from app.services import PrivateVenueService

PrivateVenueRouter = APIRouter()


@PrivateVenueRouter.get("/", response_model=list[PrivateVenue])
async def list_private_venues(
    startTime: str | None = Query(None, description="Account ID"),
    endTime: str | None = Query(None, description="Account ID"),
    session: AsyncSession = Depends(get_session),
):
    filters = {"startTime": startTime, "endTime": endTime}
    return await PrivateVenueService.list_private_venues(filters, session)


@PrivateVenueRouter.post(
    "/", response_model=PrivateVenue, status_code=status.HTTP_201_CREATED
)
async def create_private_venue(
    pv: PrivateVenueCreate, session: AsyncSession = Depends(get_session)
):
    return await PrivateVenueService.create_private_venue(pv, session)


@PrivateVenueRouter.get("/{pv_id}", response_model=PrivateVenue)
async def get_private_venue(pv_id: int, session: AsyncSession = Depends(get_session)):
    pv = await PrivateVenueService.get_private_venue(pv_id, session)
    if not pv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PrivateVenue not found"
        )
    return pv
