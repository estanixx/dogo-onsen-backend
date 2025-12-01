from typing import Optional
import uuid

from sqlmodel import Field, SQLModel, Relationship
from app.models.order import Order

class InventoryOrderBase(SQLModel):
    idOrder: str = Field(nullable=False, foreign_key="order.id")
    idItem: int = Field(nullable=False)
    quantity: int = Field(nullable=False)


class InventoryOrder(InventoryOrderBase, table=True):
    __tablename__ = "inventory_order"
    order: "Order" = Relationship(back_populates="items")
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )


class InventoryOrderCreate(InventoryOrderBase):
    pass


class InventoryOrderUpdate(SQLModel):
    idOrder: Optional[str] = None
    idItem: Optional[int] = None
    quantity: Optional[int] = None
