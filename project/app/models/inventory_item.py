from typing import Optional
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, String

class InventoryItemBase(SQLModel):
    name: str = Field(nullable=False)
    quantity: int = Field(nullable=False)
    unit: str = Field(nullable=False)


class InventoryItem(InventoryItemBase, table=True):
    __tablename__ = 'inventory_item'

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(SQLModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None