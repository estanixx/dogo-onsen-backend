from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String


class RelationType(str, Enum):
    forbidden = "forbidden"
    separation = "separation"
    allow = "allow"


class TypeRelationBase(SQLModel):
    source_type_id: str = Field(foreign_key="spirit_type.id")
    target_type_id: str = Field(foreign_key="spirit_type.id")
    relation: RelationType = Field(sa_column=Column(String, nullable=False))


class TypeRelation(TypeRelationBase, table=True):
    __tablename__ = "type_relation"
    id: Optional[int] = Field(default=None, primary_key=True)


class TypeRelationCreate(TypeRelationBase):
    pass


class TypeRelationRead(SQLModel):
    id: Optional[int]
    id_type1: str
    id_type2: str
    relation: RelationType


class TypeRelationUpdate(SQLModel):
    id_type1: Optional[str] = None
    id_type2: Optional[str] = None
    relation: Optional[RelationType] = None
