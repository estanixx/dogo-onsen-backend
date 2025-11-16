
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from app.models.service import Service
from app.models.banquet_seat import BanquetSeat
from datetime import datetime
from sqlalchemy import Column, JSON, DateTime, func


class ReservationBase(SQLModel):
    accountId: str # TODO: Relationship to VenueAccount
    startTime: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    endTime: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False)) # TODO: validate endTime > startTime
    seatId: Optional[int] = Field(default=None, foreign_key="banquet_seat.id")
    serviceId: Optional[str] = Field(default=None, foreign_key="service.id") # TODO: Arc to seat and service
    
    isRedeemed: bool = False
    isRated: bool = False
    # TODO: rating: Optional[float] = None
    # Storing account details as JSON for now (VenueAccount not modelled here)
    # TODO: account: Optional[dict] = Field(default=None, sa_column=Column(JSON), nullable=True)


class Reservation(ReservationBase, table=True):
    __tablename__ = "reservation"

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    createdAt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updatedAt: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
    )

    # Relationships
    service: Optional["Service"] = Relationship(back_populates="reservations")
    seat: Optional["BanquetSeat"] = Relationship(back_populates="reservations")


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(SQLModel):
    accountId: Optional[str] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    seatId: Optional[int] = None
    serviceId: Optional[str] = None
    isRedeemed: Optional[bool] = None
    isRated: Optional[bool] = None
    # TODO: rating: Optional[float] = None
    # TODO: account: Optional[dict] = None
