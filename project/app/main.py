import logging
logging.basicConfig(level=logging.INFO)

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.device_cookie_middleware import DeviceCookieMiddleware

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
    PrivateVenueRouter,
    UtilsRouter,
    DepositRouter,
    OrderRouter,
    InventoryOrderRouter,
)


app = FastAPI()

# Configure CORS origins via env var `CORS_ORIGINS` (comma-separated).
origins_env = os.getenv("CORS_ORIGINS")

if origins_env:
    origins = [o.strip() for o in origins_env.split(",") if o.strip()]
else:
    origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8004",
        "http://127.0.0.1:3000",
        "*",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DeviceCookieMiddleware)
app.include_router(UtilsRouter, tags=["utils"])
app.include_router(DepositRouter, prefix="/deposit", tags=["deposit"])
app.include_router(OrderRouter, prefix="/order", tags=["order"])
app.include_router(InventoryOrderRouter, prefix="/inventory_order", tags=["inventory_order"])
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
app.include_router(PrivateVenueRouter, prefix="/private_venue", tags=["private_venue"])
