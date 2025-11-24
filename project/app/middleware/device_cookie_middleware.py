import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class DeviceCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        config = None
        raw = request.cookies.get("dogo-device-config")
        if raw:
            try:
                config = json.loads(raw)
            except Exception:
                config = None

        request.state.device_config = config

        response = await call_next(request)
        return response
