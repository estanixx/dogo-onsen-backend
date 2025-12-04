from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.item_intake import ItemIntake
    from app.models.inventory_order import InventoryOrder


class ItemBase(SQLModel):
    name: str
    image: Optional[str] = None
    unit: Optional[str] = None


class Item(ItemBase, table=True):
    """Represents an inventory item that can be consumed/assigned."""

    __tablename__ = "item"
    id: Optional[int] = Field(default=None, primary_key=True)
    # One item can appear in many intakes
    intakes: List["ItemIntake"] = Relationship(back_populates="item")
    inventory_orders: List["InventoryOrder"] = Relationship(back_populates="item")

    @property
    def quantity(self) -> int:
        """
        Calculate current quantity in stock.
        Formula: sum(inventory_order.quantity WHERE redeemed=True) - sum(item_intake.quantity)
        Only counts inventory orders that have been redeemed (received).
        """
        ordered = sum(order.quantity for order in self.inventory_orders if order.redeemed)
        consumed = sum(intake.quantity for intake in self.intakes)
        return ordered - consumed


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    name: Optional[str] = None
    image: Optional[str] = None


class ItemRead(SQLModel):
    id: Optional[int]
    name: str
    image: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
