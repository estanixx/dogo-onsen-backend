from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, String

if TYPE_CHECKING:
    from app.models.spirit_type import SpiritType
    from app.models.venue_account import VenueAccount


class SpiritBase(SQLModel):
    name: str = Field(nullable=False)
    typeId: str = Field(nullable=False, foreign_key="spirit_type.id") 
    accountId: str = Field(nullable=False)
    eiltBalance: float = Field(nullable=False) 
    individualRecord: str = Field(nullable=False)
    image: Optional[str] = Field(default=None, nullable=True)
    active: Optional[bool] = Field(default=None, nullable=True) # Ok?


class Spirit(SpiritBase, table=True):
    __tablename__ = 'spirit'

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    createdAt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updatedAt: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
    )
    
    #Relationships
    type: Optional["SpiritType"] = Relationship(back_populates="spirits")
    venueAccounts: List["VenueAccount"] = Relationship(back_populates="spirit")


class SpiritCreate(SpiritBase):
    pass


class SpiritUpdate(SQLModel):
    name: Optional[str] = None
    spiritType: Optional[str] = None
    accountId: Optional[str] = None
    eiltBalance: Optional[float] = None
    individualRecord: Optional[str] = None
    image: Optional[str] = None
    active: Optional[bool] = None