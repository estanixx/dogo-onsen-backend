import pytest
from app.middleware.device_cookie_middleware import DeviceCookieMiddleware
from types import SimpleNamespace


@pytest.mark.asyncio
async def test_device_cookie_middleware_parses_cookie():
    middleware = DeviceCookieMiddleware(lambda req: SimpleNamespace())

    class Req:
        def __init__(self):
            self.cookies = {'dogo-device-config': '{"foo": "bar"}'}
            self.state = SimpleNamespace()

    async def fake_next(req):
        return SimpleNamespace(status_code=200)

    req = Req()
    res = await middleware.dispatch(req, fake_next)
    assert hasattr(req.state, 'device_config')
    assert req.state.device_config == {'foo': 'bar'}

@pytest.mark.asyncio
async def test_device_cookie_middleware_invalid_json_sets_none():
    middleware = DeviceCookieMiddleware(lambda req: SimpleNamespace())

    class Req:
        def __init__(self):
            self.cookies = {'dogo-device-config': 'not-json'}
            self.state = SimpleNamespace()

    async def fake_next(req):
        return SimpleNamespace(status_code=200)

    req = Req()
    res = await middleware.dispatch(req, fake_next)
    assert req.state.device_config is None
