
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, JSON
import uuid
from .banquet_seat import BanquetSeat

class BanquetTableBase(SQLModel):
    # Default capacity is 6 as specified in the TS interface
    capacity: int = 6
    state: bool = True


class BanquetTable(BanquetTableBase, table=True):
    """Represents a banquet table and its seats."""
    __tablename__ = "banquet_table"
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    availableSeats: List["BanquetSeat"] = Relationship(back_populates="table", sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"})
    # TODO: occupies
    


class BanquetTableCreate(BanquetTableBase):
    pass


class BanquetTableUpdate(SQLModel):
    state: Optional[bool] = None
