from typing import Optional, TYPE_CHECKING
import uuid

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.item import Item

class InventoryOrderBase(SQLModel):
    idOrder: int = Field(nullable=False, foreign_key="order.id")
    idItem: int = Field(nullable=False, foreign_key="item.id")
    quantity: int = Field(nullable=False)
    redeemed: bool = Field(default=False, nullable=False)


class InventoryOrder(InventoryOrderBase, table=True):
    __tablename__ = "inventory_order"
    order: "Order" = Relationship(back_populates="items")
    item: "Item" = Relationship(back_populates="inventory_orders")
    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True
    )


class InventoryOrderCreate(SQLModel):
    idOrder: Optional[int] = None
    idItem: int
    quantity: int
    redeemed: bool = False


class InventoryOrderUpdate(SQLModel):
    idOrder: Optional[int] = None
    idItem: Optional[int] = None
    quantity: Optional[int] = None
    redeemed: Optional[bool] = None
