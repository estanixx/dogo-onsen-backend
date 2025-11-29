from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    VenueAccount,
    VenueAccountCreate,
    VenueAccountUpdate,
    Spirit
)


class VenueAccountService:
    @staticmethod
    async def list_accounts(session: AsyncSession) -> List[VenueAccount]:
        res = await session.exec(select(VenueAccount))
        return res.all()

    @staticmethod
    async def create_account(
        account_in: VenueAccountCreate, session: AsyncSession
    ) -> VenueAccount:
        acct = VenueAccount(**account_in.dict())
        session.add(acct)
        await session.commit()
        await session.refresh(acct)
        return acct

    @staticmethod
    async def get_account(
        account_id: str, session: AsyncSession
    ) -> Optional[VenueAccount]:
        res = await session.exec(
            select(VenueAccount).where(VenueAccount.id == account_id).options(selectinload(VenueAccount.spirit).selectinload(Spirit.type))
        )
        return res.first()

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
