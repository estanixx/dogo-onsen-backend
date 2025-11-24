from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import PrivateVenue, PrivateVenueCreate
from app.services import PrivateVenueService

PrivateVenueRouter = APIRouter()


@PrivateVenueRouter.get("/", response_model=list[PrivateVenue])
async def list_private_venues(session: AsyncSession = Depends(get_session)):
    return await PrivateVenueService.list_private_venues(session)


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
