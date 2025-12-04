from typing import List, Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

from app.models.reservation import ReservationRead
from pydantic import BaseModel


class ServiceSummary(BaseModel):
    id: str
    name: str
    eiltRate: float
    image: Optional[str] = None
    description: Optional[str] = None


class ServiceWithReservations(BaseModel):
    service: ServiceSummary
    reservations_count: int


class TableAvailability(BaseModel):
    id: int
    capacity: int
    takenSeats: int
    availableSeats: int


class DashboardRead(BaseModel):
    today_reservations_per_service: List[ServiceWithReservations]
    today_occupancy_rate: float
    stock_alerts: int
    pending_orders: int
    today_table_availability: List[TableAvailability]


class DateRequest(BaseModel):
    date: str


class DateTimeRequest(BaseModel):
    datetime: str
