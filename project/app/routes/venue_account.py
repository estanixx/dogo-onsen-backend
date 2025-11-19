from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import VenueAccount, VenueAccountCreate, VenueAccountUpdate
from app.services import VenueAccountService

VenueAccountRouter = APIRouter()


@VenueAccountRouter.get("/", response_model=list[VenueAccount])
async def list_accounts(session: AsyncSession = Depends(get_session)):
    return await VenueAccountService.list_accounts(session)


@VenueAccountRouter.post(
    "/", response_model=VenueAccount, status_code=status.HTTP_201_CREATED
)
async def create_account(
    account_in: VenueAccountCreate, session: AsyncSession = Depends(get_session)
):
    return await VenueAccountService.create_account(account_in, session)


@VenueAccountRouter.get("/{account_id}", response_model=VenueAccount)
async def get_account(account_id: str, session: AsyncSession = Depends(get_session)):
    acct = await VenueAccountService.get_account(account_id, session)
    if not acct:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Venue account not found"
        )
    return acct


@VenueAccountRouter.put("/{account_id}", response_model=VenueAccount)
async def update_account(
    account_id: str,
    account_in: VenueAccountUpdate,
    session: AsyncSession = Depends(get_session),
):
    acct = await VenueAccountService.update_account(account_id, account_in, session)
    if not acct:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Venue account not found"
        )
    return acct


@VenueAccountRouter.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: str, session: AsyncSession = Depends(get_session)):
    ok = await VenueAccountService.delete_account(account_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Venue account not found"
        )
    return None
