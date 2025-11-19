import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Employee, EmployeeCreate, EmployeeUpdate
from app.services import EmployeeService

EmployeeRouter = APIRouter()


@EmployeeRouter.get("/", response_model=list[Employee])
async def list_employees(
    estado: str | None = Query(default=None, description="Filter by estado"),
    clerk_id: str | None = Query(default=None, description="Filter by Clerk user ID"),
    session: AsyncSession = Depends(get_session),
):
    return await EmployeeService.list_employees(
        session, estado=estado, clerk_id=clerk_id
    )


@EmployeeRouter.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_in: EmployeeCreate, session: AsyncSession = Depends(get_session)
):
    return await EmployeeService.create_employee(employee_in, session)


@EmployeeRouter.get("/{clerk_id}", response_model=Employee)
async def get_employee(clerk_id: str, session: AsyncSession = Depends(get_session)):
    return await EmployeeService.get_employee_or_404(clerk_id, session)


@EmployeeRouter.get("/clerk/{clerk_id}", response_model=Employee)
async def get_employee_by_clerk_id(
    clerk_id: str, session: AsyncSession = Depends(get_session)
):
    return await EmployeeService.get_employee_or_404(clerk_id, session)


@EmployeeRouter.put("/{clerk_id}", response_model=Employee)
async def update_employee(
    clerk_id: str,
    employee_update: EmployeeUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await EmployeeService.update_employee(clerk_id, employee_update, session)


@EmployeeRouter.delete("/{clerk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(clerk_id: str, session: AsyncSession = Depends(get_session)):
    await EmployeeService.delete_employee(clerk_id, session)
    return None


@EmployeeRouter.post("/webhook/clerk")
async def clerk_webhook(
    request: Request,
    svix_signature: str | None = Header(None, alias="svix-signature"),
    svix_timestamp: str | None = Header(None, alias="svix-timestamp"),
    session: AsyncSession = Depends(get_session),
):
    body = await request.body()

    secret = os.getenv("CLERK_WEBHOOK_SECRET")
    if not secret or not svix_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing signature"
        )

    payload = await request.json()
    return await EmployeeService.process_clerk_webhook(payload, session)
