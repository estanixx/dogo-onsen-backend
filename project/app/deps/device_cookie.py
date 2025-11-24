from typing import Optional

from fastapi import Request
from pydantic import BaseModel


class DeviceConfig(BaseModel):
    type: Optional[str] = None
    roomId: Optional[str] = None


async def get_device_config(request: Request) -> Optional[DeviceConfig]:
    cfg = getattr(request.state, "device_config", None)
    if not cfg:
        return None
    try:
        return DeviceConfig(**cfg)
    except Exception:
        return None
