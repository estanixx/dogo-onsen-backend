import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    ServiceRouter,
    EmployeeRouter,
    BanquetRouter,
    ReservationRouter,
    SpiritRouter,
    SpiritTypeRouter,
    FileRouter,
    VenueAccountRouter,
    ItemRouter,
    ItemIntakeRouter,
    UtilsRouter,
)

app = FastAPI()

# Configure CORS origins via env var `CORS_ORIGINS` (comma-separated).
# If not provided, allow common localhost dev origins.
origins_env = os.getenv("CORS_ORIGINS")

if origins_env:
    origins = [o.strip() for o in origins_env.split(",") if o.strip()]
else:
    origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8004",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UtilsRouter, tags=["utils"])
app.include_router(ServiceRouter, prefix="/service", tags=["service"])
app.include_router(EmployeeRouter, prefix="/employee", tags=["employee"])
app.include_router(BanquetRouter, prefix="/banquet", tags=["banquet"])
app.include_router(ReservationRouter, prefix="/reservation", tags=["reservation"])
app.include_router(SpiritRouter, prefix="/spirit", tags=["spirit"])
app.include_router(SpiritTypeRouter, prefix="/spirit_type", tags=["spirit_type"])
app.include_router(FileRouter, prefix="/files", tags=["files"])
app.include_router(VenueAccountRouter, prefix="/venue_account", tags=["venue_account"])
app.include_router(ItemRouter, prefix="/item", tags=["item"])
app.include_router(ItemIntakeRouter, prefix="/item_intake", tags=["item_intake"])