from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, String

from app.models.spirit_type import SpiritType
if TYPE_CHECKING:
    from app.models.venue_account import VenueAccount


class SpiritBase(SQLModel):
    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    typeId: str = Field(nullable=False, foreign_key="spirit_type.id") 
    # accountId: str = Field(nullable=False)

    # individualRecord: str = Field(nullable=False)
    image: Optional[str] = Field(default=None, nullable=False)
    active: bool = Field(default=True, nullable=False)


class Spirit(SpiritBase, table=True):
    __tablename__ = 'spirit'

    createdAt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updatedAt: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
    )
    
    #Relationships
    type: "SpiritType" = Relationship(back_populates="spirits")
    venueAccounts: List["VenueAccount"] = Relationship(back_populates="spirit")


class SpiritCreate(SpiritBase):
    pass

class SpiritUpdate(SQLModel):
    name: Optional[str] = None
    spiritType: Optional[str] = None
    # accountId: Optional[str] = None
    # individualRecord: Optional[str] = None
    image: Optional[str] = None
    active: Optional[bool] = None

class SpiritRead(SpiritBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    type: "SpiritType"
    currentlyInVenue: Optional[bool] = None