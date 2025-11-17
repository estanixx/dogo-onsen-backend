
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column

if TYPE_CHECKING:
    from app.models.banquet_table import BanquetTable
    from .reservation import Reservation


class BanquetSeatBase(SQLModel):
    seatNumber: int


class BanquetSeat(BanquetSeatBase, table=True):
    """Represents an individual seat at a banquet table."""
    __tablename__ = "banquet_seat"
    id: Optional[int] = Field(default=None, primary_key=True)
    # Foreign key to BanquetTable id (string UUID)
    tableId: str = Field(foreign_key="banquet_table.id", nullable=False)
    table: "BanquetTable" = Relationship(back_populates="availableSeats")
    # One seat can have many reservations
    reservations: List["Reservation"] = Relationship(back_populates="seat")


class BanquetSeatCreate(BanquetSeatBase):
    tableId: str


class BanquetSeatUpdate(SQLModel):
    seatNumber: Optional[int] = None
    # TODO: rationsConsumed: Optional[int] = None
    tableId: Optional[str] = None


class BanquetSeatRead(SQLModel):
    id: Optional[int]
    tableId: str
    seatNumber: int


