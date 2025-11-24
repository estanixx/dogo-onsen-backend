from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Column, Integer

if TYPE_CHECKING:
    from app.models.venue_account import VenueAccount


class PrivateVenueBase(SQLModel):
    pass


class PrivateVenue(PrivateVenueBase, table=True):
    __tablename__ = "private_venue"
    id: Optional[int] = Field(default=None, primary_key=True)

    # One private venue can have many venue accounts
    venueAccounts: List["VenueAccount"] = Relationship(back_populates="privateVenue")


class PrivateVenueCreate(PrivateVenueBase):
    id: Optional[int] = None


class PrivateVenueRead(SQLModel):
    id: Optional[str]
