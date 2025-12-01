from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.type_relation import (
    TypeRelation,
    TypeRelationCreate,
    TypeRelationUpdate,
)


class TypeRelationService:
    @staticmethod
    async def list_type_relations(session: AsyncSession) -> List[TypeRelation]:
        res = await session.exec(select(TypeRelation))
        return res.all()

    @staticmethod
    async def create_type_relation(
        tr_in: TypeRelationCreate, session: AsyncSession
    ) -> TypeRelation:
        tr = TypeRelation(**tr_in.dict())
        session.add(tr)
        await session.commit()
        await session.refresh(tr)
        return tr

    @staticmethod
    async def get_type_relation(
        tr_id: int, session: AsyncSession
    ) -> Optional[TypeRelation]:
        res = await session.exec(select(TypeRelation).where(TypeRelation.id == tr_id))
        return res.first()

    @staticmethod
    async def update_type_relation(
        tr_id: int, tr_in: TypeRelationUpdate, session: AsyncSession
    ) -> Optional[TypeRelation]:
        res = await session.exec(select(TypeRelation).where(TypeRelation.id == tr_id))
        tr = res.first()
        if not tr:
            return None
        data = tr_in.dict(exclude_unset=True)
        # support both the model field names and older id_type1/id_type2 keys
        if "id_type1" in data:
            data["source_type_id"] = data.pop("id_type1")
        if "id_type2" in data:
            data["target_type_id"] = data.pop("id_type2")
        for key, value in data.items():
            setattr(tr, key, value)
        session.add(tr)
        await session.commit()
        await session.refresh(tr)
        return tr

    @staticmethod
    async def delete_type_relation(tr_id: int, session: AsyncSession) -> bool:
        res = await session.exec(select(TypeRelation).where(TypeRelation.id == tr_id))
        tr = res.first()
        if not tr:
            return False
        await session.delete(tr)
        await session.commit()
        return True

    @staticmethod
    async def get_relation_between(
        source_type_id: str, target_type_id: str, session: AsyncSession
    ) -> Optional[TypeRelation]:
        """
        Return the TypeRelation between two spirit types.

        This first attempts to find a direct relation where `source_type_id`
        maps to `target_type_id`. If none is found, it also checks the
        inverse direction (useful if relations were added in either order).
        If still none found, returns None.
        """
        res = await session.exec(
            select(TypeRelation).where(
                (TypeRelation.source_type_id == source_type_id)
                & (TypeRelation.target_type_id == target_type_id)
            )
        )
        tr = res.first()
        if tr:
            return tr

        # Try inverse
        res = await session.exec(
            select(TypeRelation).where(
                (TypeRelation.source_type_id == target_type_id)
                & (TypeRelation.target_type_id == source_type_id)
            )
        )
        return res.first()
