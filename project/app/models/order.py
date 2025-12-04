from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime

if TYPE_CHECKING:
    from app.models.inventory_order import InventoryOrder


class OrderBase(SQLModel):
    idEmployee: str = Field(nullable=False)
    orderDate: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deliveryDate: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Order(OrderBase, table=True):
    __tablename__ = "order"

    id: int | None = Field(default=None, primary_key=True)
    
    items: List["InventoryOrder"] = Relationship(back_populates="order")


class OrderCreate(OrderBase):
    pass


class OrderUpdate(SQLModel):
    idEmployee: Optional[str] = None
    # orderDate: Optional[datetime] = None #Esto no se debería actualizar supongo
    deliveryDate: Optional[datetime] = None


# Response models for serialization
class InventoryOrderInOrder(SQLModel):
    idOrder: int
    idItem: int
    quantity: int
    redeemed: Optional[bool] = None


class OrderRead(OrderBase):
    id: int
    items: List[InventoryOrderInOrder] = []
