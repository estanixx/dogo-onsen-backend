from app.core.seed import run_seeds
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
import os
from app.db import get_session
import json
from app.services import ServiceService, PrivateVenueService, BanquetService
from app.models.utils import DashboardRead
from datetime import datetime, timezone


UtilsRouter = APIRouter()


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

    dashboard = DashboardRead(
        today_reservations_per_service=services_data,
        today_occupancy_rate=occupancy,
        stock_alerts=0,
        pending_orders=0,
        today_table_availability=table_taken,
    )
    return dashboard
