from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime, func, String

if TYPE_CHECKING:
    from app.models.spirit import Spirit

class SpiritTypeBase(SQLModel):
    name: str = Field(nullable=False)
    kanji: str = Field(nullable=False)
    dangerScore: int = Field(nullable=False)
    image: str = Field(nullable=False)

class SpiritType(SpiritTypeBase, table=True):
    __tablename__ = 'spirit_type'

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Esto hay que ponerlo?
    spirits: List["Spirit"] = Relationship(back_populates="type")


class SpiritTypeCreate(SpiritTypeBase):
    pass


class SpiritTypeUpdate(SQLModel):
    name: Optional[str] = None
    dangerScore: Optional[int] = None
    image: Optional[str] = None