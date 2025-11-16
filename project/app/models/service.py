from sqlmodel import SQLModel, Field
from typing import Optional
import uuid


class ServiceBase(SQLModel):
    name: str
    eiltRate: float
    image: Optional[str] = None


class Service(ServiceBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)


class ServiceCreate(ServiceBase):
    pass