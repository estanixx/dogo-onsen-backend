import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, JSON, DateTime, UniqueConstraint, func
from sqlmodel import SQLModel, Field


class EmployeeBase(SQLModel):
    clerkId: str = Field(index=True, nullable=False)
    emailAddress: str = Field(index=True, nullable=False)
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None
    imageUrl: Optional[str] = None
    role: str = Field(default='reception', nullable=False)
    accessStatus: str = Field(default='pending', nullable=False)
    organizationIds: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False, server_default='[]'),
    )


class Employee(EmployeeBase, table=True):
    __tablename__ = 'employee'
    __table_args__ = (
        UniqueConstraint('clerkId', name='uq_employee_clerk_id'),
        UniqueConstraint('emailAddress', name='uq_employee_email'),
    )

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


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(SQLModel):
    clerkId: Optional[str] = None
    emailAddress: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None
    imageUrl: Optional[str] = None
    role: Optional[str] = None
    accessStatus: Optional[str] = None
    organizationIds: Optional[List[str]] = None
