from typing import List, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class EmployeeBase(SQLModel):
    estado: str = Field(default='pendiente', nullable=False)
    tareasAsignadas: List[str] = Field(
        default_factory=list,
        sa_column=Column('tareas_asignadas', JSON, nullable=False, server_default='[]'),
    )


class Employee(EmployeeBase, table=True):
    __tablename__ = 'employee'

    clerkId: str = Field(primary_key=True, index=True, nullable=False)


class EmployeeCreate(EmployeeBase):
    clerkId: str


class EmployeeUpdate(SQLModel):
    estado: Optional[str] = None
    tareasAsignadas: Optional[List[str]] = None
