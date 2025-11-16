from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.employee import Employee, EmployeeCreate, EmployeeUpdate

EmployeeRouter = APIRouter()


def _apply_employee_filters(statement, role: str | None, access_status: str | None, clerk_id: str | None):
    if role:
        statement = statement.where(Employee.role == role)
    if access_status:
        statement = statement.where(Employee.accessStatus == access_status)
    if clerk_id:
        statement = statement.where(Employee.clerkId == clerk_id)
    return statement


@EmployeeRouter.get("/", response_model=list[Employee])
async def list_employees(
    role: str | None = Query(default=None, description="Filter by role"),
    access_status: str | None = Query(default=None, description="Filter by access status"),
    clerk_id: str | None = Query(default=None, description="Filter by Clerk user ID"),
    session: AsyncSession = Depends(get_session),
):
    statement = select(Employee).order_by(Employee.createdAt.desc())
    statement = _apply_employee_filters(statement, role, access_status, clerk_id)
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


@EmployeeRouter.get("/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str, session: AsyncSession = Depends(get_session)):
    employee = await _get_employee_or_404(employee_id, session)
    return employee


@EmployeeRouter.get("/clerk/{clerk_id}", response_model=Employee)
async def get_employee_by_clerk_id(clerk_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Employee).where(Employee.clerkId == clerk_id))
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@EmployeeRouter.put("/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: str,
    employee_update: EmployeeUpdate,
    session: AsyncSession = Depends(get_session),
):
    employee = await _get_employee_or_404(employee_id, session)

    update_data = employee_update.dict(exclude_unset=True)

    if 'clerkId' in update_data and update_data['clerkId'] != employee.clerkId:
        await _ensure_clerk_id_is_unique(update_data['clerkId'], session)

    if 'emailAddress' in update_data and update_data['emailAddress'] != employee.emailAddress:
        await _ensure_email_is_unique(update_data['emailAddress'], session)

    for key, value in update_data.items():
        setattr(employee, key, value)

    employee.updatedAt = datetime.utcnow()

    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


@EmployeeRouter.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: str, session: AsyncSession = Depends(get_session)):
    employee = await _get_employee_or_404(employee_id, session)
    await session.delete(employee)
    await session.commit()
    return None


async def _get_employee_or_404(employee_id: str, session: AsyncSession) -> Employee:
    result = await session.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


async def _ensure_employee_is_unique(employee_in: EmployeeCreate, session: AsyncSession) -> None:
    await _ensure_clerk_id_is_unique(employee_in.clerkId, session)
    await _ensure_email_is_unique(employee_in.emailAddress, session)


async def _ensure_clerk_id_is_unique(clerk_id: str, session: AsyncSession) -> None:
    result = await session.execute(select(Employee).where(Employee.clerkId == clerk_id))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already exists with this Clerk ID",
        )


async def _ensure_email_is_unique(email: str, session: AsyncSession) -> None:
    result = await session.execute(select(Employee).where(Employee.emailAddress == email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already exists with this email",
        )