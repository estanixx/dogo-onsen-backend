import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.employee import Employee, EmployeeCreate, EmployeeUpdate

EmployeeRouter = APIRouter()


def _extract_user_from_payload(payload: dict) -> dict:
    # Clerk webhook payload may nest the user in different keys. Try common locations.
    if not payload:
        return {}
    if isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("object"), dict):
        return payload["data"]["object"]
    if isinstance(payload.get("user"), dict):
        return payload["user"]
    if isinstance(payload.get("object"), dict):
        return payload["object"]
    # fallback: maybe payload itself is the user
    return payload


def _map_clerk_user_to_employee_payload(user: dict) -> dict:
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


def _apply_employee_filters(statement, estado: str | None, clerk_id: str | None):
    if estado:
        statement = statement.where(Employee.estado == estado)
    if clerk_id:
        statement = statement.where(Employee.clerkId == clerk_id)
    return statement


@EmployeeRouter.get("/", response_model=list[Employee])
async def list_employees(
    estado: str | None = Query(default=None, description="Filter by estado"),
    clerk_id: str | None = Query(default=None, description="Filter by Clerk user ID"),
    session: AsyncSession = Depends(get_session),
):
    statement = select(Employee).order_by(Employee.clerkId.asc())
    statement = _apply_employee_filters(statement, estado, clerk_id)
    result = await session.execute(statement)
    return result.scalars().all()


@EmployeeRouter.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
async def create_employee(employee_in: EmployeeCreate, session: AsyncSession = Depends(get_session)):
    await _ensure_employee_is_unique(employee_in, session)

    employee = Employee(**employee_in.dict())
    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


@EmployeeRouter.get("/{clerk_id}", response_model=Employee)
async def get_employee(clerk_id: str, session: AsyncSession = Depends(get_session)):
    employee = await _get_employee_or_404(clerk_id, session)
    return employee


@EmployeeRouter.get("/clerk/{clerk_id}", response_model=Employee)
async def get_employee_by_clerk_id(clerk_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Employee).where(Employee.clerkId == clerk_id))
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@EmployeeRouter.put("/{clerk_id}", response_model=Employee)
async def update_employee(
    clerk_id: str,
    employee_update: EmployeeUpdate,
    session: AsyncSession = Depends(get_session),
):
    employee = await _get_employee_or_404(clerk_id, session)

    update_data = employee_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)

    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


@EmployeeRouter.delete("/{clerk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(clerk_id: str, session: AsyncSession = Depends(get_session)):
    employee = await _get_employee_or_404(clerk_id, session)
    await session.delete(employee)
    await session.commit()
    return None


async def _get_employee_or_404(clerk_id: str, session: AsyncSession) -> Employee:
    result = await session.execute(select(Employee).where(Employee.clerkId == clerk_id))
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


async def _ensure_employee_is_unique(employee_in: EmployeeCreate, session: AsyncSession) -> None:
    await _ensure_clerk_id_is_unique(employee_in.clerkId, session)


async def _ensure_clerk_id_is_unique(clerk_id: str, session: AsyncSession) -> None:
    result = await session.execute(select(Employee).where(Employee.clerkId == clerk_id))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already exists with this Clerk ID",
        )



# Webhook endpoint for Clerk to sync users into the employee table.
# If CLERK_WEBHOOK_SECRET is set, the header 'Clerk-Signature' must match the
# HMAC-SHA256 of the raw request body using that secret. If not set, signature
# verification is skipped (useful for local testing).
@EmployeeRouter.post("/webhook/clerk")
async def clerk_webhook(
    request: Request,
    clerk_signature: str | None = Header(None, alias="Clerk-Signature"),
    session: AsyncSession = Depends(get_session),
):
    body = await request.body()

    secret = os.getenv("CLERK_WEBHOOK_SECRET")
    if secret:
        if not clerk_signature:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing signature")
        import hmac, hashlib

        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        # allow signature header to contain the hex directly or in a prefixed form
        if expected != clerk_signature and expected not in (s.strip() for s in clerk_signature.split(",")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    payload = await request.json()
    user = _extract_user_from_payload(payload)
    if not user or not user.get("id"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload: user not found")

    emp_payload = _map_clerk_user_to_employee_payload(user)

    # Upsert: find existing by clerkId, else create
    result = await session.execute(select(Employee).where(Employee.clerkId == emp_payload["clerkId"]))
    existing = result.scalars().first()
    if existing:
        # update fields
        for k, v in emp_payload.items():
            setattr(existing, k, v)
        session.add(existing)
        await session.commit()
        await session.refresh(existing)
        return {"ok": True, "action": "updated", "clerkId": emp_payload["clerkId"]}

    # create new employee
    new_emp = Employee(**emp_payload)
    session.add(new_emp)
    await session.commit()
    await session.refresh(new_emp)
    return {"ok": True, "action": "created", "clerkId": emp_payload["clerkId"]}