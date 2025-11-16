import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import ServiceRouter, EmployeeRouter


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

app.include_router(ServiceRouter, prefix="/service", tags=["service"])
app.include_router(EmployeeRouter, prefix="/employee", tags=["employee"])


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}
