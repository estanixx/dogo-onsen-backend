from app.core.seed import run_seeds
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
import os
from app.db import get_session


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