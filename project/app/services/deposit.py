from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.deposit import Deposit, DepositCreate, DepositUpdate


class DepositService:
    @staticmethod
    async def list_deposits(session: AsyncSession) -> List[Deposit]:
        res = await session.exec(select(Deposit))
        return res.all()

    @staticmethod
    async def create_deposit(
        deposit_in: DepositCreate, session: AsyncSession
    ) -> Deposit:
        st = Deposit(**deposit_in.dict())
        session.add(st)
        await session.commit()
        await session.refresh(st)
        return st

    @staticmethod
    async def get_deposit(
        deposit_id: str, session: AsyncSession
    ) -> Optional[Deposit]:
        res = await session.exec(
            select(Deposit).where(Deposit.id == deposit_id)
        )
        return res.first()

    @staticmethod
    async def update_deposit(
        deposit_id: str, deposit_in: DepositUpdate, session: AsyncSession
    ) -> Optional[Deposit]:
        res = await session.exec(
            select(Deposit).where(Deposit.id == deposit_id)
        )
        st = res.first()
        if not st:
            return None
        data = deposit_in.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(st, key, value)
        session.add(st)
        await session.commit()
        await session.refresh(st)
        return st

    @staticmethod
    async def delete_deposit(deposit_id: str, session: AsyncSession) -> bool:
        res = await session.exec(
            select(Deposit).where(Deposit.id == deposit_id)
        )
        st = res.first()
        if not st:
            return False
        await session.delete(st)
        await session.commit()
        return True
