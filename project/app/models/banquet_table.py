
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, JSON
import uuid
from .banquet_seat import BanquetSeat, BanquetSeatRead, AvailableBanquetSeatRead
if TYPE_CHECKING:
    from app.models.spirit import Spirit

class BanquetTableBase(SQLModel):
    # Default capacity is 6 as specified in the TS interface
    capacity: int = 6
    state: bool = True


class BanquetTable(BanquetTableBase, table=True):
    """Represents a banquet table and its seats."""
    __tablename__ = "banquet_table"
    id: int = Field(default=None, primary_key=True)
    availableSeats: List["BanquetSeat"] = Relationship(back_populates="table", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    
    


class BanquetTableCreate(BanquetTableBase):
    pass


class BanquetTableUpdate(SQLModel):
    state: Optional[bool] = None


class BanquetTableRead(SQLModel):
    id: int
    capacity: int = 6
    state: bool = True
    availableSeats: Optional[List[BanquetSeatRead]] = None


class AvailableBanquetTableRead(BanquetTableRead):
    availableSeats: Optional[List[AvailableBanquetSeatRead]] = None
    occupies: Optional[List[dict]] = None
