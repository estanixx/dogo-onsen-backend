import os
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header, status
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models import Employee, EmployeeCreate, EmployeeUpdate
from app.services import EmployeeService
from app.services.clerk_api import ClerkAPIService
from app.core.admin_auth import AdminAuthService, verify_admin

EmployeeRouter = APIRouter()


# Pydantic models for admin endpoints
class AdminLoginRequest(BaseModel):
    clerk_id: str


class AdminLoginResponse(BaseModel):
    token: str
    message: str


class EmployeeWithUserInfo(BaseModel):
    clerk_id: str
    first_name: str
    last_name: str
    email: str
    role: str
    estado: str
    is_admin: bool = False


class UpdateEmployeeStatusRequest(BaseModel):
    estado: str  # Should be 'approved' or 'revoked'


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


# ============ ADMIN ENDPOINTS ============

@EmployeeRouter.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Admin login endpoint. Verifies that the user has admin role in Clerk.
    Returns a JWT token for subsequent admin requests.
    """
    try:
        # Get user data from Clerk API
        user_data = await ClerkAPIService.get_user(request.clerk_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in Clerk"
            )
        
        # Check if user has admin role
        public_meta = user_data.get("public_metadata") or {}
        role = public_meta.get("role")
        
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have admin privileges"
            )
        
        # Create admin token
        token = AdminAuthService.create_admin_token(request.clerk_id)
        
        return AdminLoginResponse(
            token=token,
            message="Admin login successful"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during admin login: {str(e)}"
        )


@EmployeeRouter.get("/admin/employees", response_model=list[EmployeeWithUserInfo])
async def admin_list_employees(
    admin_payload: Dict[str, Any] = Depends(verify_admin),
    session: AsyncSession = Depends(get_session),
):
    """
    List all employees with their information.
    Only accessible to authenticated admins.
    Uses data stored in database (synced from Clerk webhook).
    """
    try:
        # Get all employees from database
        statement = select(Employee).order_by(Employee.clerkId.asc())
        result = await session.exec(statement)
        employees = result.all()
        
        # Map to response model using stored data
        enriched_employees = []
        for emp in employees:
            # Try to get admin status from Clerk
            is_admin = False
            try:
                user_data = await ClerkAPIService.get_user(emp.clerkId)
                if user_data:
                    public_meta = user_data.get("public_metadata") or {}
                    is_admin = public_meta.get("role") == "admin"
            except Exception as e:
                # Log but don't fail if we can't check Clerk
                print(f"Warning: Could not check admin status for {emp.clerkId}: {str(e)}")
            
            enriched_employees.append(
                EmployeeWithUserInfo(
                    clerk_id=emp.clerkId,
                    first_name=emp.firstName or "",
                    last_name=emp.lastName or "",
                    email=emp.email or "",
                    role="reception",  # Default role, stored in Clerk publicMetadata
                    estado=emp.estado,
                    is_admin=is_admin
                )
            )
        
        return enriched_employees
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing employees: {str(e)}"
        )


@EmployeeRouter.put("/admin/employees/{clerk_id}/status", response_model=Employee)
async def admin_update_employee_status(
    clerk_id: str,
    status_update: UpdateEmployeeStatusRequest,
    admin_payload: Dict[str, Any] = Depends(verify_admin),
    session: AsyncSession = Depends(get_session),
):
    """
    Update employee status (approve or revoke).
    Only accessible to authenticated admins.
    Allowed status values: 'approved', 'revoked'
    """
    # Validate status
    if status_update.estado not in ["approved", "revoked", "pendiente"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'approved', 'revoked', or 'pendiente'"
        )
    
    try:
        # Update employee estado
        employee_update = EmployeeUpdate(estado=status_update.estado)
        updated_employee = await EmployeeService.update_employee(
            clerk_id,
            employee_update,
            session
        )
        
        return updated_employee
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating employee status: {str(e)}"
        )


@EmployeeRouter.post("/admin/sync-from-clerk", response_model=Dict[str, Any])
async def admin_sync_from_clerk(
    admin_payload: Dict[str, Any] = Depends(verify_admin),
    session: AsyncSession = Depends(get_session),
):
    """
    Sync all users from Clerk to the database.
    Only accessible to authenticated admins.
    """
    try:
        # Get all users from Clerk
        users = await ClerkAPIService.list_users()
        
        if not users:
            return {
                "ok": True,
                "message": "No users found in Clerk",
                "synced_count": 0,
                "updated_count": 0
            }
        
        synced_count = 0
        updated_count = 0
        
        for user in users:
            try:
                clerk_id = user.get("id")
                if not clerk_id:
                    continue
                
                emp_payload = EmployeeService._map_clerk_user_to_employee_payload(user)
                
                # Check if employee already exists
                result = await session.exec(
                    select(Employee).where(Employee.clerkId == clerk_id)
                )
                existing = result.first()
                
                if existing:
                    # Update existing employee
                    for key, value in emp_payload.items():
                        setattr(existing, key, value)
                    session.add(existing)
                    updated_count += 1
                else:
                    # Create new employee
                    new_emp = Employee(**emp_payload)
                    session.add(new_emp)
                    synced_count += 1
            
            except Exception as e:
                # Log error but continue with other users
                print(f"Error syncing user {user.get('id')}: {str(e)}")
                continue
        
        # Commit all changes
        await session.commit()
        
        return {
            "ok": True,
            "message": f"Synced {synced_count} new users and updated {updated_count} existing users",
            "synced_count": synced_count,
            "updated_count": updated_count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing users from Clerk: {str(e)}"
        )


@EmployeeRouter.put("/admin/employees/{clerk_id}/make-admin", response_model=Dict[str, Any])
async def admin_make_employee_admin(
    clerk_id: str,
    admin_payload: Dict[str, Any] = Depends(verify_admin),
    session: AsyncSession = Depends(get_session),
):
    """
    Set an employee as admin in Clerk public_metadata.
    Only accessible to authenticated admins.
    """
    try:
        # Make the API call to Clerk to set admin role
        import httpx
        
        secret_key = os.getenv("CLERK_SECRET_KEY")
        if not secret_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="CLERK_SECRET_KEY not configured"
            )
        
        url = f"https://api.clerk.com/v1/users/{clerk_id}"
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "public_metadata": {
                "role": "admin"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=payload, headers=headers, timeout=10.0)
            
            if response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to update user in Clerk: {response.text}"
                )
        
        # Update the local database as well
        employee_update = EmployeeUpdate()
        await EmployeeService.update_employee(clerk_id, employee_update, session)
        
        return {
            "ok": True,
            "message": f"User {clerk_id} is now an admin",
            "clerk_id": clerk_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating admin status: {str(e)}"
        )
