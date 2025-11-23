from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, String

from app.models.spirit import Spirit
if TYPE_CHECKING:
    from app.models.reservation import Reservation

class VenueAccountBase(SQLModel):
    # TODO: Add attributes
    spiritId: str = Field(foreign_key="spirit.id")
    


class VenueAccount(VenueAccountBase, table=True):
    __tablename__ = 'venue_account'
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Esto hay que ponerlo?
    reservations: List["Reservation"] = Relationship(back_populates="account")
    spirit: "Spirit" = Relationship(back_populates="venueAccounts")
    pin: str = Field(nullable=False)
    



class VenueAccountCreate(VenueAccountBase):
    pass


class VenueAccountUpdate(SQLModel):
    # TODO: Complete
    spiritId: Optional[str] = None