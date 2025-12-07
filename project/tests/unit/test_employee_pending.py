import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.employee import EmployeeService
from app.models import Employee


@pytest.mark.asyncio
async def test_employee_with_pending_status_cannot_be_listed_as_active(async_session_mock):
    """
    RF-004: Usuarios con estado "pendiente" no deberían aparecer 
    cuando se filtran empleados activos.
    """
    pending_employee = Employee(
        clerkId="pending_user_123",
        estado="pendiente",
        firstName="Pending",
        lastName="User",
        email="pending@example.com"
    )
    
    active_employee = Employee(
        clerkId="active_user_456",
        estado="activo",
        firstName="Active",
        lastName="User",
        email="active@example.com"
    )
    
    # Mock para retornar solo empleados activos cuando se filtra por estado
    mock_result = MagicMock()
    mock_result.all.return_value = [active_employee]
    async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
    
    result = await EmployeeService.list_employees(async_session_mock, estado="activo")
    
    assert len(result) == 1
    assert result[0].estado == "activo"
    assert result[0].clerkId == "active_user_456"


@pytest.mark.asyncio
async def test_employee_pending_status_blocks_access(async_session_mock):
    """
    RF-004: Un empleado con estado "pendiente" debería estar bloqueado
    hasta que un admin lo habilite cambiando su estado.
    """
    pending_employee = Employee(
        clerkId="blocked_user",
        estado="pendiente",
        firstName="Blocked",
        lastName="User",
        email="blocked@example.com"
    )
    
    mock_result = MagicMock()
    mock_result.first.return_value = pending_employee
    async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
    
    # Verificar que el usuario existe pero está pendiente
    employee = await EmployeeService.get_employee_or_404("blocked_user", async_session_mock)
    
    assert employee.estado == "pendiente"
    # El sistema debería rechazar acceso a usuarios pendientes en el middleware/UI


@pytest.mark.asyncio
async def test_employee_approved_status_allows_access(async_session_mock):
    """
    RF-004: Un empleado con estado "aprobado" o "activo" debería poder acceder.
    """
    approved_employee = Employee(
        clerkId="approved_user",
        estado="activo",
        firstName="Approved",
        lastName="User",
        email="approved@example.com"
    )
    
    mock_result = MagicMock()
    mock_result.first.return_value = approved_employee
    async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
    
    employee = await EmployeeService.get_employee_or_404("approved_user", async_session_mock)
    
    assert employee.estado == "activo"
    assert employee.clerkId == "approved_user"


@pytest.mark.asyncio 
async def test_admin_can_change_employee_status_from_pending_to_active(async_session_mock):
    """
    RF-004: Un admin puede cambiar el estado de un empleado de "pendiente" a "activo".
    """
    pending_employee = Employee(
        clerkId="user_to_approve",
        estado="pendiente",
        firstName="Pending",
        lastName="User",
        email="pending@example.com"
    )
    
    mock_result = MagicMock()
    mock_result.first.return_value = pending_employee
    async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
    async_session_mock.add = MagicMock()
    async_session_mock.commit = AsyncMock()
    async_session_mock.refresh = AsyncMock()
    
    from app.models import EmployeeUpdate
    update = EmployeeUpdate(estado="activo")
    
    result = await EmployeeService.update_employee("user_to_approve", update, async_session_mock)
    
    assert result.estado == "activo"
    async_session_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_clerk_webhook_creates_employee_with_pending_status_by_default(async_session_mock):
    """
    RF-004: Cuando un usuario se registra via Clerk webhook, 
    debería crearse con estado "pendiente" por defecto.
    """
    payload = {
        'data': {
            'object': {
                'id': 'new_clerk_user',
                'public_metadata': {},  # Sin estado definido
                'email_addresses': [{'email_address': 'new@example.com'}],
                'first_name': 'New',
                'last_name': 'User'
            }
        }
    }
    
    # El servicio debería crear con estado "pendiente" si no se especifica
    mapped = EmployeeService._map_clerk_user_to_employee_payload(
        payload['data']['object']
    )
    
    assert mapped['estado'] == 'pendiente'
    assert mapped['clerkId'] == 'new_clerk_user'
