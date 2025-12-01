from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Deposit, DepositCreate, DepositUpdate
from app.services import DepositService

DepositRouter = APIRouter()


@DepositRouter.get("/", response_model=list[Deposit])
async def list_deposits(session: AsyncSession = Depends(get_session)):
    return await DepositService.list_deposits(session)


@DepositRouter.get("/account/{account_id}", response_model=list[Deposit])
async def list_deposits_for_account(
    account_id: str, session: AsyncSession = Depends(get_session)
):
    """Return deposits filtered by venue account id"""
    return await DepositService.list_deposits_for_account(account_id, session)


@DepositRouter.post("/", response_model=Deposit, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit: DepositCreate, session: AsyncSession = Depends(get_session)
):
    return await DepositService.create_deposit(deposit, session)


@DepositRouter.get("/{deposit_id}", response_model=Deposit)
async def get_deposit(deposit_id: str, session: AsyncSession = Depends(get_session)):
    d = await DepositService.get_deposit(deposit_id, session)
    if not d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deposit not found"
        )
    return d


@DepositRouter.put("/{deposit_id}", response_model=Deposit)
async def update_deposit(
    deposit_id: str,
    deposit: DepositUpdate,
    session: AsyncSession = Depends(get_session),
):
    d = await DepositService.update_deposit(deposit_id, deposit, session)
    if not d:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deposit not found"
        )
    return d


@DepositRouter.delete("/{deposit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deposit(deposit_id: str, session: AsyncSession = Depends(get_session)):
    ok = await DepositService.delete_deposit(deposit_id, session)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Deposit not found"
        )
    return None
