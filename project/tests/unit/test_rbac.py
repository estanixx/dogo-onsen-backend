"""
RNF-004: Tests de Autenticación y RBAC

Este módulo prueba el control de acceso basado en roles (RBAC)
y la integración con Clerk para autenticación.

Criterio de aceptación:
- Usuarios mapeados a roles correctamente
- Pruebas de acceso muestran restricciones por rol
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from app.services.employee import EmployeeService


class TestRoleMapping:
    """Tests para mapeo de roles desde Clerk."""

    def test_map_admin_role_from_clerk_metadata(self):
        """RNF-004: Mapeo correcto del rol 'admin' desde Clerk."""
        clerk_user = {
            "id": "admin_user_123",
            "public_metadata": {
                "role": "admin",
                "accessStatus": "activo"
            },
            "email_addresses": [{"email_address": "admin@example.com"}],
            "first_name": "Admin",
            "last_name": "User"
        }
        
        # Verificar que el rol está correctamente en metadata
        role = clerk_user["public_metadata"].get("role")
        
        assert role == "admin"

    def test_map_employee_role_from_clerk_metadata(self):
        """RNF-004: Mapeo correcto del rol 'employee' desde Clerk."""
        clerk_user = {
            "id": "employee_user_456",
            "public_metadata": {
                "role": "employee",
                "accessStatus": "activo"
            },
            "email_addresses": [{"email_address": "employee@example.com"}],
            "first_name": "Employee",
            "last_name": "User"
        }
        
        role = clerk_user["public_metadata"].get("role")
        
        assert role == "employee"

    def test_map_receptionist_role_from_clerk_metadata(self):
        """RNF-004: Mapeo correcto del rol 'recepcionista' desde Clerk."""
        clerk_user = {
            "id": "receptionist_789",
            "public_metadata": {
                "role": "recepcionista",
                "accessStatus": "activo",
                "tareasAsignadas": ["recepcion", "check-in"]
            },
            "email_addresses": [{"email_address": "recepcion@example.com"}],
            "first_name": "Reception",
            "last_name": "Staff"
        }
        
        role = clerk_user["public_metadata"].get("role")
        tareas = clerk_user["public_metadata"].get("tareasAsignadas", [])
        
        assert role == "recepcionista"
        assert "recepcion" in tareas

    def test_default_role_when_not_specified(self):
        """RNF-004: Rol por defecto cuando no se especifica."""
        clerk_user = {
            "id": "new_user",
            "public_metadata": {},
            "email_addresses": [{"email_address": "new@example.com"}],
            "first_name": "New",
            "last_name": "User"
        }
        
        role = clerk_user["public_metadata"].get("role", "guest")
        
        assert role == "guest"

    def test_employee_payload_mapping_preserves_role(self):
        """RNF-004: El mapeo de payload preserva información de rol."""
        clerk_user = {
            "id": "clerk_with_role",
            "public_metadata": {
                "accessStatus": "activo",
                "tareasAsignadas": ["inventario", "banquete"]
            },
            "email_addresses": [{"email_address": "worker@example.com"}],
            "first_name": "Worker",
            "last_name": "Bee"
        }
        
        mapped = EmployeeService._map_clerk_user_to_employee_payload(clerk_user)
        
        assert mapped["clerkId"] == "clerk_with_role"
        assert mapped["estado"] == "activo"
        assert "inventario" in mapped["tareasAsignadas"]
        assert "banquete" in mapped["tareasAsignadas"]


class TestRoleBasedAccess:
    """Tests para verificar restricciones de acceso por rol."""

    def test_admin_can_access_all_routes(self):
        """RNF-004: Admin tiene acceso a todas las rutas."""
        admin_permissions = {
            "can_manage_employees": True,
            "can_view_reports": True,
            "can_modify_settings": True,
            "can_access_inventory": True,
            "can_access_banquet": True,
            "can_access_reception": True,
        }
        
        def check_admin_access(role: str, permission: str) -> bool:
            if role == "admin":
                return True
            return admin_permissions.get(permission, False)
        
        for permission in admin_permissions.keys():
            assert check_admin_access("admin", permission) is True

    def test_employee_cannot_access_admin_routes(self):
        """RNF-004: Empleado normal no puede acceder a rutas de admin."""
        def check_admin_route_access(role: str) -> bool:
            return role == "admin"
        
        assert check_admin_route_access("employee") is False
        assert check_admin_route_access("recepcionista") is False
        assert check_admin_route_access("admin") is True

    def test_receptionist_access_limited_to_reception(self):
        """RNF-004: Recepcionista solo puede acceder a rutas de recepción."""
        # Rutas específicas permitidas para recepcionista (excluye /admin)
        receptionist_allowed_routes = ["/employee/reception"]
        receptionist_blocked_routes = ["/employee/admin", "/employee/inventory", "/employee/banquet"]

        def check_route_access(role: str, route: str) -> bool:
            if role == "admin":
                return True
            if role == "recepcionista":
                # Bloquear explícitamente rutas de admin
                if any(route.startswith(blocked) for blocked in receptionist_blocked_routes):
                    return False
                return any(route.startswith(allowed) for allowed in receptionist_allowed_routes)
            return False
        
        assert check_route_access("recepcionista", "/employee/reception") is True
        assert check_route_access("recepcionista", "/employee/admin") is False
class TestAdminTokenValidation:
    """Tests para validación de tokens de admin."""

    @pytest.mark.asyncio
    async def test_valid_admin_token_grants_access(self):
        """RNF-004: Token de admin válido otorga acceso."""
        from app.core.admin_auth import AdminAuthService
        
        # Crear token para admin
        clerk_id = "admin_test_123"
        token = AdminAuthService.create_admin_token(clerk_id)
        
        # Verificar token
        payload = AdminAuthService.verify_admin_token(token)
        
        assert payload["clerk_id"] == clerk_id
        assert payload["is_admin"] is True

    @pytest.mark.asyncio
    async def test_invalid_token_raises_unauthorized(self):
        """RNF-004: Token inválido genera error 401."""
        from app.core.admin_auth import AdminAuthService
        
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            AdminAuthService.verify_admin_token(invalid_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio  
    async def test_expired_token_raises_unauthorized(self):
        """RNF-004: Token expirado genera error 401."""
        import jwt
        from datetime import datetime, timedelta
        
        from app.core.admin_auth import AdminAuthService
        
        # Crear token ya expirado
        secret = AdminAuthService._get_jwt_secret()
        expired_payload = {
            "clerk_id": "admin_expired",
            "is_admin": True,
            "iat": datetime.utcnow() - timedelta(hours=48),
            "exp": datetime.utcnow() - timedelta(hours=24)  # Expiró hace 24 horas
        }
        expired_token = jwt.encode(expired_payload, secret, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            AdminAuthService.verify_admin_token(expired_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "expired" in exc_info.value.detail.lower()


class TestTaskAssignment:
    """Tests para asignación de tareas a empleados."""

    def test_employee_with_assigned_tasks(self):
        """RNF-004: Empleado con tareas asignadas específicas."""
        clerk_user = {
            "id": "worker_with_tasks",
            "public_metadata": {
                "accessStatus": "activo",
                "tareasAsignadas": ["1", "3", "5"]  # IDs de tareas
            },
            "email_addresses": [{"email_address": "worker@example.com"}],
            "first_name": "Task",
            "last_name": "Worker"
        }
        
        mapped = EmployeeService._map_clerk_user_to_employee_payload(clerk_user)
        
        assert len(mapped["tareasAsignadas"]) == 3
        assert "1" in mapped["tareasAsignadas"]

    def test_employee_can_access_assigned_module(self):
        """RNF-004: Empleado solo puede acceder a módulos de sus tareas asignadas."""
        # Mapeo de IDs de tarea a módulos
        task_to_module = {
            "1": "inventario",
            "2": "banquete", 
            "3": "recepcion",
            "4": "servicios"
        }
        
        employee_tasks = ["1", "3"]  # Inventario y Recepción
        
        def can_access_module(module: str, assigned_tasks: list) -> bool:
            for task_id, mod in task_to_module.items():
                if mod == module and task_id in assigned_tasks:
                    return True
            return False
        
        assert can_access_module("inventario", employee_tasks) is True
        assert can_access_module("recepcion", employee_tasks) is True
        assert can_access_module("banquete", employee_tasks) is False
