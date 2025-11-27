from typing import Optional
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, String

class DepositBase(SQLModel):
    accountId: str = Field(nullable=False)
    amount: int = Field(nullable=False)
    date: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))


class Deposit(DepositBase, table=True):
    __tablename__ = 'deposit'

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)


class DepositCreate(DepositBase):
    pass


class DepositUpdate(SQLModel):
    accountId: Optional[str] = None
    amount: Optional[int] = None
    date: Optional[datetime] = None