from typing import Optional, List, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.models import Employee, EmployeeCreate, EmployeeUpdate


class EmployeeService:
    @staticmethod
    async def list_employees(
        session: AsyncSession,
        estado: Optional[str] = None,
        clerk_id: Optional[str] = None,
    ) -> List[Employee]:
        statement = select(Employee).order_by(Employee.clerkId.asc())
        if estado:
            statement = statement.where(Employee.estado == estado)
        if clerk_id:
            statement = statement.where(Employee.clerkId == clerk_id)
        result = await session.exec(statement)
        return result.scalars().all()

    @staticmethod
    async def create_employee(
        employee_in: EmployeeCreate, session: AsyncSession
    ) -> Employee:
        await EmployeeService._ensure_employee_is_unique(employee_in, session)
        employee = Employee(**employee_in.dict())
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        return employee

    @staticmethod
    async def get_employee_or_404(clerk_id: str, session: AsyncSession) -> Employee:
        result = await session.exec(
            select(Employee).where(Employee.clerkId == clerk_id)
        )
        employee = result.scalars().first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
            )
        return employee

    @staticmethod
    async def update_employee(
        clerk_id: str, employee_update: EmployeeUpdate, session: AsyncSession
    ) -> Employee:
        employee = await EmployeeService.get_employee_or_404(clerk_id, session)
        update_data = employee_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(employee, key, value)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        return employee

    @staticmethod
    async def delete_employee(clerk_id: str, session: AsyncSession) -> None:
        employee = await EmployeeService.get_employee_or_404(clerk_id, session)
        await session.delete(employee)
        await session.commit()

    @staticmethod
    async def _ensure_employee_is_unique(
        employee_in: EmployeeCreate, session: AsyncSession
    ) -> None:
        await EmployeeService._ensure_clerk_id_is_unique(employee_in.clerkId, session)

    @staticmethod
    async def _ensure_clerk_id_is_unique(clerk_id: str, session: AsyncSession) -> None:
        result = await session.exec(
            select(Employee).where(Employee.clerkId == clerk_id)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee already exists with this Clerk ID",
            )

    @staticmethod
    def _extract_user_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not payload:
            return {}
        data = payload.get("data")
        if isinstance(data, dict):
            obj = data.get("object")
            if isinstance(obj, dict):
                return obj
            if data.get("id"):
                return data
        if isinstance(payload.get("user"), dict):
            return payload["user"]
        if isinstance(payload.get("object"), dict):
            return payload["object"]
        return payload

    @staticmethod
    def _map_clerk_user_to_employee_payload(user: Dict[str, Any]) -> Dict[str, Any]:
        public_meta = user.get("public_metadata") or {}
        estado = public_meta.get("estado") or "pendiente"
        tareas = public_meta.get("tareasAsignadas") or []
        if not isinstance(tareas, list):
            tareas = []
        tareas = [str(item) for item in tareas]

        return {
            "clerkId": user.get("id"),
            "estado": estado,
            "tareasAsignadas": tareas,
        }

    @staticmethod
    async def process_clerk_webhook(
        payload: Dict[str, Any], session: AsyncSession
    ) -> Dict[str, Any]:
        user = EmployeeService._extract_user_from_payload(payload)
        if not user or not user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook payload: user not found",
            )

        emp_payload = EmployeeService._map_clerk_user_to_employee_payload(user)

        result = await session.exec(
            select(Employee).where(Employee.clerkId == emp_payload["clerkId"])
        )
        existing = result.scalars().first()
        if existing:
            for key, value in emp_payload.items():
                setattr(existing, key, value)
            session.add(existing)
            await session.commit()
            await session.refresh(existing)
            return {"ok": True, "action": "updated", "clerkId": emp_payload["clerkId"]}

        new_emp = Employee(**emp_payload)
        session.add(new_emp)
        await session.commit()
        await session.refresh(new_emp)
        return {"ok": True, "action": "created", "clerkId": emp_payload["clerkId"]}
