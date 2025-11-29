from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, String
from app.models.spirit import Spirit, SpiritRead

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.private_venue import PrivateVenue


class VenueAccountBase(SQLModel):
    # TODO: Add attributes
    spiritId: str = Field(foreign_key="spirit.id")
    privateVenueId: int = Field(foreign_key="private_venue.id")
    startTime: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    endTime: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class VenueAccount(VenueAccountBase, table=True):
    __tablename__ = "venue_account"
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )

    # Esto hay que ponerlo?
    reservations: List["Reservation"] = Relationship(back_populates="account")
    spirit: "Spirit" = Relationship(back_populates="venueAccounts")
    privateVenue: "PrivateVenue" = Relationship(back_populates="venueAccounts")
    pin: str = Field(nullable=False)

class VenueAccountRead(VenueAccountBase):
    id: Optional[str]
    spiritId: str
    privateVenueId: int
    startTime: datetime
    endTime: datetime
    pin: str
    spirit: "SpiritRead"

class VenueAccountCreate(VenueAccountBase):
    pass


class VenueAccountUpdate(SQLModel):
    # TODO: Complete
    spiritId: Optional[str] = None
