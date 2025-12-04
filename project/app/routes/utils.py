from app.core.seed import run_seeds
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
import os
from app.db import get_session
from sqlmodel import select
import json
from app.services import ServiceService, PrivateVenueService, BanquetService, ItemService
from sqlalchemy import func, distinct
from app.models import Order, InventoryOrder
from app.models.utils import DashboardRead
from datetime import datetime, timezone
import logging


UtilsRouter = APIRouter()

logger = logging.getLogger(__name__)


@UtilsRouter.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@UtilsRouter.get("/seed")
async def seed_database(session: AsyncSession = Depends(get_session)):
    if os.getenv("ENV") != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Database seeding is only allowed in development environment",
        )
    # Implement your seeding logic here
    status = await run_seeds(session)
    return {"status": status}


@UtilsRouter.get("/device-config")
async def get_device_config(request: Request):
    """Return parsed device configuration stored in httpOnly cookie `dogo-device-config`.

    Returns 204 if cookie is not present or invalid.
    """
    raw = request.cookies.get("dogo-device-config")
    if not raw:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    try:
        cfg = json.loads(raw)
    except Exception:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return cfg


@UtilsRouter.get("/time-slots", response_model=list[str])
async def get_time_slots():
    """Return available time slots for reservations."""
    from app.core.constants import TIME_SLOTS

    return TIME_SLOTS


@UtilsRouter.get("/dashboard", response_model=DashboardRead)
async def get_dashboard(session: AsyncSession = Depends(get_session)):
    # Today in UTC

    services_data = await ServiceService.today_reservations_per_service(session)
    occupancy = await PrivateVenueService.today_occupancy_rate(session)
    table_taken = await BanquetService.today_table_availability(session)

    # Compute stock alerts and pending orders; wrap in try/except so endpoint
    # always returns valid JSON even if something goes wrong.
    try:
        # Compute stock alerts: count of items whose calculated `quantity` is below threshold
        items = await ItemService.list_items(session)
        STOCK_THRESHOLD = 12
        # Coerce quantities safely and log them for debugging
        stock_alerts = 0
        for it in items:
            # support both attribute access and dict-like objects
            q = getattr(it, 'quantity', None)
            if q is None and isinstance(it, dict):
                q = it.get('quantity')
            try:
                qnum = int(q) if q is not None else 0
            except Exception:
                qnum = 0
            logger.debug('dashboard item quantity', extra={
                'item_id': getattr(it, 'id', None) or it.get('id') if isinstance(it, dict) else getattr(it, 'id', None),
                'item_name': getattr(it, 'name', None) or (it.get('name') if isinstance(it, dict) else None),
                'quantity': qnum,
            })
            if qnum < STOCK_THRESHOLD:
                stock_alerts += 1

        # Compute pending orders: number of distinct orders that have at least one inventory line not redeemed
        stmt = (
            select(func.count(distinct(Order.id)))
            .select_from(Order)
            .join(InventoryOrder, InventoryOrder.idOrder == Order.id)
            .where(InventoryOrder.redeemed == False)
        )
        res = await session.exec(stmt)
        # `.scalar_one()` may not be available on the returned result object in some SQLModel/SQLAlchemy versions.
        # Use `.first()` and extract the first column safely.
        row = res.first()
        if row is None:
            pending_orders = 0
        else:
            # row can be a Row or scalar depending on driver; try to extract first element
            try:
                val = row[0]
            except Exception:
                val = row
            pending_orders = int(val or 0)
    except Exception as e:
        logger.exception('Error computing dashboard metrics')
        stock_alerts = 0
        pending_orders = 0

    dashboard = DashboardRead(
        today_reservations_per_service=services_data,
        today_occupancy_rate=occupancy,
        stock_alerts=stock_alerts,
        pending_orders=pending_orders,
        today_table_availability=table_taken,
    )
    return dashboard
