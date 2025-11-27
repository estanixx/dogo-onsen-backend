from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime
from sqlalchemy import Column, JSON, DateTime, func
if TYPE_CHECKING:
    from app.models.reservation import Reservation


class ServiceBase(SQLModel):
    name: str
    eiltRate: float
    image: Optional[str] = None
    rating: float = 0.0


class Service(ServiceBase, table=True):
    reservations: List["Reservation"] = Relationship(back_populates="service")
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    createdAt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updatedAt: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(SQLModel):
    name: Optional[str] = None
    eiltRate: Optional[float] = None
    image: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None

