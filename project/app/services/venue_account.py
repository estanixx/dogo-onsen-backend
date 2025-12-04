from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from datetime import datetime
from fastapi import HTTPException, status
from app.models import (
    VenueAccount,
    VenueAccountCreate,
    VenueAccountUpdate,
    VenueAccountRead,
    Spirit,
    Deposit,
    Reservation,
    Service,
)


class VenueAccountService:
    @staticmethod
    async def _compute_account_balance(
        acct: VenueAccount, session: AsyncSession
    ) -> float:
        # Compute balance for this account (deposits - consumption)
        dep_q = select(func.coalesce(func.sum(Deposit.amount), 0)).where(
            Deposit.accountId == acct.id
        )
        dep_res = await session.exec(dep_q)
        try:
            total_deposits = float(dep_res.one())
        except Exception:
            total_deposits = float(dep_res.scalar_one() or 0)

        cons_q = (
            select(func.coalesce(func.sum(Service.eiltRate), 0))
            .select_from(Reservation)
            .join(Service, Reservation.serviceId == Service.id)
            .where(Reservation.accountId == acct.id)
        )
        cons_res = await session.exec(cons_q)
        try:
            total_consumed = float(cons_res.one())
        except Exception:
            total_consumed = float(cons_res.scalar_one() or 0)
        return total_deposits - total_consumed

    @staticmethod
    async def get_current_account_for_room(
        room_id: int, session: AsyncSession
    ) -> Optional[VenueAccountRead]:
        res = await session.exec(
            select(VenueAccount)
            .where(
                VenueAccount.privateVenueId == room_id,
                VenueAccount.startTime <= datetime.now(),
                VenueAccount.endTime >= datetime.now(),
            )
            .options(selectinload(VenueAccount.spirit).selectinload(Spirit.type))
        )
        acct = res.first()
        if not acct:
            return None

        acct = VenueAccountRead.from_orm(acct)
        acct.eiltBalance = await VenueAccountService._compute_account_balance(
            acct, session
        )

        return acct

    @staticmethod
    async def list_accounts(session: AsyncSession) -> List[VenueAccountRead]:
        # Eager-load related models so Pydantic serialization won't trigger
        # lazy IO (which causes MissingGreenlet errors).
        res = await session.exec(
            select(VenueAccount).options(
                selectinload(VenueAccount.spirit).selectinload(Spirit.type)
            )
        )
        accts = res.all()

        out: List[VenueAccountRead] = []
        for acct in accts:
            read = VenueAccountRead.from_orm(acct)
            # Compute balance inside the async context to avoid lazy DB IO
            read.eiltBalance = await VenueAccountService._compute_account_balance(
                acct, session
            )
            out.append(read)

        return out

    @staticmethod
    async def create_account(
        account_in: VenueAccountCreate, session: AsyncSession
    ) -> VenueAccount:
        # Ensure the same spirit doesn't already have an overlapping account
        start_dt = account_in.startTime
        end_dt = account_in.endTime
        overlap_q = select(VenueAccount).where(
            (VenueAccount.spiritId == account_in.spiritId)
            & (VenueAccount.startTime < end_dt)
            & (VenueAccount.endTime > start_dt)
        )
        res = await session.exec(overlap_q)
        if res.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una cuenta para este espíritu en el período especificado.",
            )

        acct = VenueAccount(**account_in.dict())
        session.add(acct)
        await session.commit()
        await session.refresh(acct)
        return acct

    @staticmethod
    async def get_account(
        account_id: str, session: AsyncSession
    ) -> Optional[VenueAccountRead]:
        res = await session.exec(
            select(VenueAccount)
            .where(VenueAccount.id == account_id)
            .options(selectinload(VenueAccount.spirit).selectinload(Spirit.type))
        )
        acct = res.first()
        if not acct:
            return None
        acct = VenueAccountRead.from_orm(acct)
        acct.eiltBalance = await VenueAccountService._compute_account_balance(
            acct, session
        )
        return acct

    @staticmethod
    async def update_account(
        account_id: str, account_in: VenueAccountUpdate, session: AsyncSession
    ) -> Optional[VenueAccount]:
        res = await session.exec(
            select(VenueAccount).where(VenueAccount.id == account_id)
        )
        acct = res.first()
        if not acct:
            return None
        data = account_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(acct, key, value)
        session.add(acct)
        await session.commit()
        await session.refresh(acct)
        return acct

    @staticmethod
    async def delete_account(account_id: str, session: AsyncSession) -> bool:
        res = await session.exec(
            select(VenueAccount).where(VenueAccount.id == account_id)
        )
        acct = res.first()
        if not acct:
            return False
        await session.delete(acct)
        await session.commit()
        return True
