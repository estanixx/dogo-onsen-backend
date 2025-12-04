from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import inspect
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
    def quantity(self) -> int | None:
        """
        Calculate current quantity in stock.
        Formula: sum(inventory_order.quantity WHERE redeemed=True) - sum(item_intake.quantity)
        Only counts inventory orders that have been redeemed (received).
        """
        # Avoid triggering lazy loads while Pydantic/Response serialization runs.
        # If the necessary relationships are not already loaded, return None so the
        # response layer doesn't attempt IO here (which causes MissingGreenlet).
        state = inspect(self)
        if not (state.attrs.inventory_orders.loaded and state.attrs.intakes.loaded):
            return None

        ordered = sum(order.quantity for order in self.inventory_orders if getattr(order, "redeemed", False))

        consumed = 0
        for intake in self.intakes:
            # if intake is tied to a service, we need that service and its reservations
            if getattr(intake, "serviceId", None):
                intake_state = inspect(intake)
                # If the service relation or its reservations aren't loaded, assume 0 reservations
                # (i.e. no consumption) to avoid triggering lazy loads during serialization.
                if not intake_state.attrs.service.loaded:
                    num_res = 0
                else:
                    svc = intake.service
                    svc_state = inspect(svc)
                    if not svc_state.attrs.reservations.loaded:
                        num_res = 0
                    else:
                        num_res = len(svc.reservations) or 0
                consumed += intake.quantity * num_res
            else:
                # seat-based or generic intake: counts once
                consumed += intake.quantity

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
