from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.item_intake import ItemIntake


class ItemBase(SQLModel):
    name: str
    image: Optional[str] = None


class Item(ItemBase, table=True):
    """Represents an inventory item that can be consumed/assigned."""

    __tablename__ = "item"
    id: Optional[int] = Field(default=None, primary_key=True)
    # One item can appear in many intakes
    intakes: List["ItemIntake"] = Relationship(back_populates="item")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    name: Optional[str] = None
    image: Optional[str] = None


class ItemRead(SQLModel):
    id: Optional[int]
    name: str
    image: Optional[str] = None
