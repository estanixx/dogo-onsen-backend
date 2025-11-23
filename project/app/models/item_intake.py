from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from pydantic import root_validator

if TYPE_CHECKING:
    from app.models.banquet_seat import BanquetSeat
    from app.models.service import Service
    from app.models.item import Item


class ItemIntakeBase(SQLModel):
    quantity: int
    itemId: int
    seatId: Optional[int] = None
    serviceId: Optional[str] = None

    @root_validator
    def seat_xor_service(cls, values):
        seat = values.get("seatId")
        service = values.get("serviceId")
        if seat is not None and service is not None:
            raise ValueError(
                "`seatId` and `serviceId` cannot both be set at the same time"
            )
        return values


class ItemIntake(ItemIntakeBase, table=True):
    """Represents a quantity of an Item assigned either to a banquet seat or to a service."""

    __tablename__ = "item_intake"
    id: Optional[int] = Field(default=None, primary_key=True)
    itemId: int = Field(foreign_key="item.id", nullable=False)
    seatId: Optional[int] = Field(default=None, foreign_key="banquet_seat.id")
    serviceId: Optional[str] = Field(default=None, foreign_key="service.id")

    # Relationships
    item: "Item" = Relationship(back_populates="intakes")
    seat: Optional["BanquetSeat"] = Relationship()
    service: Optional["Service"] = Relationship()


class ItemIntakeCreate(ItemIntakeBase):
    pass


class ItemIntakeUpdate(SQLModel):
    quantity: Optional[int] = None
    itemId: Optional[int] = None
    seatId: Optional[int] = None
    serviceId: Optional[str] = None


class ItemIntakeRead(SQLModel):
    id: Optional[int]
    itemId: int
    seatId: Optional[int]
    serviceId: Optional[str]
    quantity: int
