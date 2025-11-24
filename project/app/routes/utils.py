from app.core.seed import run_seeds
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
import os
from app.db import get_session
import json


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
    await run_seeds(session)
    return {"status": "database seeded successfully"}


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