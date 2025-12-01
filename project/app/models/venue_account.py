from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, String
from app.models.spirit import Spirit, SpiritRead
import secrets


from app.core.tools import logger

# root validators not used here

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.private_venue import PrivateVenue
    from app.models.deposit import Deposit


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
    # eiltBalance: float = Field(nullable=False) TODO: Calcular, total depositos - total consumo
    # eiltBalance is computed (total deposits - total consumption) and
    # provided on read models by the service layer.


class VenueAccount(VenueAccountBase, table=True):
    __tablename__ = "venue_account"
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )
    deposits: List["Deposit"] = Relationship(back_populates="account")

    # Esto hay que ponerlo?
    reservations: List["Reservation"] = Relationship(back_populates="account")
    spirit: "Spirit" = Relationship(back_populates="venueAccounts")
    privateVenue: "PrivateVenue" = Relationship(back_populates="venueAccounts")
    pin: str = Field(
        default_factory=lambda: f"{secrets.randbelow(10**6):06d}", nullable=False
    )
    # model-specific validators not required here
    # model-specific validators not required here


class VenueAccountRead(VenueAccountBase):
    id: Optional[str]
    spiritId: str
    privateVenueId: int
    startTime: datetime
    endTime: datetime
    pin: str
    spirit: "SpiritRead"
    eiltBalance: float = Field(default=0.0)

    class Config:
        from_attributes = True
        validate_by_name = True


class VenueAccountCreate(VenueAccountBase):
    pass


class VenueAccountUpdate(SQLModel):
    # TODO: Complete
    spiritId: Optional[str] = None
