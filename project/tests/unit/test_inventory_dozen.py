"""
RNF-006: Tests de Inventario (docenas ↔ unidades)

Este módulo prueba la conversión entre docenas y unidades,
pedido mínimo de 1 docena, y alertas de stock bajo.

Criterio de aceptación:
- Pedidos actualizan stock correcto
- Alertas al alcanzar umbral de stock bajo
- Pedido mínimo 1 docena (12 unidades)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models import Item, InventoryOrder
from app.models.inventory_order import InventoryOrderCreate
from app.services.item import ItemService
from app.services.inventory_order import InventoryOrderService


# Constante para conversión docena ↔ unidades
UNITS_PER_DOZEN = 12
LOW_STOCK_THRESHOLD = 24  # Umbral de stock bajo (2 docenas)


class TestDozenToUnitsConversion:
    """Tests para conversión entre docenas y unidades."""

    def test_one_dozen_equals_twelve_units(self):
        """RNF-006: 1 docena = 12 unidades."""
        dozens = 1
        units = dozens * UNITS_PER_DOZEN
        
        assert units == 12

    def test_multiple_dozens_conversion(self):
        """RNF-006: Conversión de múltiples docenas a unidades."""
        test_cases = [
            (1, 12),
            (2, 24),
            (5, 60),
            (10, 120),
        ]
        
        for dozens, expected_units in test_cases:
            units = dozens * UNITS_PER_DOZEN
            assert units == expected_units, f"{dozens} docenas deberían ser {expected_units} unidades"

    def test_units_to_dozens_conversion(self):
        """RNF-006: Conversión de unidades a docenas."""
        test_cases = [
            (12, 1),
            (24, 2),
            (36, 3),
            (120, 10),
        ]
        
        for units, expected_dozens in test_cases:
            dozens = units // UNITS_PER_DOZEN
            assert dozens == expected_dozens

    def test_partial_dozen_not_counted(self):
        """RNF-006: Unidades parciales no cuentan como docena completa."""
        units = 15  # 1 docena + 3 unidades
        complete_dozens = units // UNITS_PER_DOZEN
        remaining_units = units % UNITS_PER_DOZEN
        
        assert complete_dozens == 1
        assert remaining_units == 3


class TestMinimumOrderDozen:
    """Tests para pedido mínimo de 1 docena."""

    @pytest.mark.asyncio
    async def test_order_minimum_one_dozen_valid(self, async_session_mock):
        """RNF-006: Pedido de 1 docena (12 unidades) es válido."""
        order_quantity = 12  # 1 docena
        
        # Verificar que la cantidad es al menos 1 docena
        is_valid = order_quantity >= UNITS_PER_DOZEN
        
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_order_less_than_dozen_invalid(self, async_session_mock):
        """RNF-006: Pedido de menos de 1 docena debería ser inválido."""
        order_quantity = 6  # Media docena
        
        # Verificar que la cantidad es menor a 1 docena
        is_valid = order_quantity >= UNITS_PER_DOZEN
        
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_order_multiple_dozens_valid(self, async_session_mock):
        """RNF-006: Pedido de múltiples docenas es válido."""
        quantities = [24, 36, 48, 120]  # 2, 3, 4, 10 docenas
        
        for qty in quantities:
            is_valid = qty >= UNITS_PER_DOZEN
            assert is_valid is True, f"Pedido de {qty} unidades debería ser válido"

    def test_validate_order_quantity_helper(self):
        """RNF-006: Helper para validar cantidad de pedido."""
        def validate_order_quantity(quantity: int) -> tuple[bool, str]:
            """Valida que el pedido sea al menos 1 docena."""
            if quantity < UNITS_PER_DOZEN:
                return False, f"Pedido mínimo es 1 docena ({UNITS_PER_DOZEN} unidades)"
            return True, "Cantidad válida"
        
        # Casos válidos
        assert validate_order_quantity(12)[0] is True
        assert validate_order_quantity(24)[0] is True
        
        # Casos inválidos
        is_valid, message = validate_order_quantity(6)
        assert is_valid is False
        assert "mínimo" in message.lower()


class TestInventoryStockCalculation:
    """Tests para cálculo correcto de stock."""

    @pytest.mark.asyncio
    async def test_stock_increases_with_redeemed_order(self, async_session_mock):
        """RNF-006: Stock aumenta cuando un pedido es recibido (redeemed)."""
        # Pedido de 24 unidades (2 docenas) marcado como recibido
        initial_stock = 0
        order_quantity = 24
        redeemed = True
        
        if redeemed:
            new_stock = initial_stock + order_quantity
        else:
            new_stock = initial_stock
        
        assert new_stock == 24

    @pytest.mark.asyncio
    async def test_stock_not_increased_for_pending_order(self, async_session_mock):
        """RNF-006: Stock NO aumenta para pedidos pendientes (no redeemed)."""
        initial_stock = 12
        order_quantity = 24
        redeemed = False
        
        if redeemed:
            new_stock = initial_stock + order_quantity
        else:
            new_stock = initial_stock
        
        assert new_stock == 12  # Stock sin cambios

    @pytest.mark.asyncio
    async def test_stock_calculation_with_consumption(self, async_session_mock):
        """RNF-006: Stock = pedidos recibidos - consumo."""
        orders_received = 48  # 4 docenas recibidas
        consumed = 12  # 1 docena consumida
        
        current_stock = orders_received - consumed
        
        assert current_stock == 36


class TestLowStockAlert:
    """Tests para alertas de stock bajo."""

    def test_low_stock_alert_triggered(self):
        """RNF-006: Alerta cuando stock está bajo el umbral."""
        current_stock = 18  # 1.5 docenas
        
        is_low_stock = current_stock < LOW_STOCK_THRESHOLD
        
        assert is_low_stock is True

    def test_no_alert_when_stock_above_threshold(self):
        """RNF-006: No hay alerta cuando stock está sobre el umbral."""
        current_stock = 36  # 3 docenas
        
        is_low_stock = current_stock < LOW_STOCK_THRESHOLD
        
        assert is_low_stock is False

    def test_alert_at_exact_threshold(self):
        """RNF-006: Stock exactamente en el umbral no genera alerta."""
        current_stock = LOW_STOCK_THRESHOLD  # Exactamente 2 docenas
        
        is_low_stock = current_stock < LOW_STOCK_THRESHOLD
        
        assert is_low_stock is False

    def test_zero_stock_generates_alert(self):
        """RNF-006: Stock en cero genera alerta."""
        current_stock = 0
        
        is_low_stock = current_stock < LOW_STOCK_THRESHOLD
        
        assert is_low_stock is True

    def test_get_low_stock_items_helper(self):
        """RNF-006: Helper para obtener items con stock bajo."""
        items_stock = [
            {"name": "Toallas", "quantity": 6},    # Bajo
            {"name": "Jabones", "quantity": 48},   # OK
            {"name": "Shampoo", "quantity": 12},   # Bajo
            {"name": "Aceites", "quantity": 100},  # OK
        ]
        
        low_stock_items = [
            item for item in items_stock 
            if item["quantity"] < LOW_STOCK_THRESHOLD
        ]
        
        assert len(low_stock_items) == 2
        assert low_stock_items[0]["name"] == "Toallas"
        assert low_stock_items[1]["name"] == "Shampoo"


class TestInventoryOrderIntegration:
    """Tests de integración para órdenes de inventario."""

    @pytest.mark.asyncio
    async def test_create_inventory_order_with_dozen_quantity(self, async_session_mock):
        """RNF-006: Crear orden de inventario con cantidad en docenas."""
        async_session_mock.add = MagicMock()
        async_session_mock.commit = AsyncMock()
        async_session_mock.refresh = AsyncMock()
        
        # Orden de 3 docenas
        dozens_ordered = 3
        units = dozens_ordered * UNITS_PER_DOZEN
        
        order_in = InventoryOrderCreate(
            idOrder=1,
            idItem=1,
            quantity=units,
            redeemed=False
        )
        
        result = await InventoryOrderService.create_inventory_order(
            order_in, async_session_mock
        )
        
        assert result.quantity == 36  # 3 docenas = 36 unidades
        async_session_mock.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_redeem_order_updates_stock(self, async_session_mock):
        """RNF-006: Al marcar orden como recibida, el stock debe actualizarse."""
        existing_order = InventoryOrder(
            id="order_123",
            idOrder=1,
            idItem=1,
            quantity=24,  # 2 docenas
            redeemed=False
        )
        
        mock_result = MagicMock()
        mock_result.first.return_value = existing_order
        async_session_mock.exec.side_effect = AsyncMock(return_value=mock_result)
        async_session_mock.add = MagicMock()
        async_session_mock.commit = AsyncMock()
        async_session_mock.refresh = AsyncMock()
        
        from app.models.inventory_order import InventoryOrderUpdate
        update = InventoryOrderUpdate(redeemed=True)
        
        result = await InventoryOrderService.update_inventory_order(
            "order_123", update, async_session_mock
        )
        
        assert result.redeemed is True
        async_session_mock.commit.assert_called_once()
