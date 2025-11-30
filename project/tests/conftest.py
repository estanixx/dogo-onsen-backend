import sys
import pathlib
import warnings
import pytest
from unittest.mock import AsyncMock, MagicMock


# Ensure project root is on sys.path so `import app` works when running pytest from `project/`
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def async_session_mock():
    """Provide a simple mocked AsyncSession with common methods used by services."""
    session = MagicMock()
    # exec should be async and return an object with .all() and .first()
    async def fake_exec(q):
        m = MagicMock()
        m.all = MagicMock(return_value=[])
        m.first = MagicMock(return_value=None)
        return m

    session.exec = AsyncMock(side_effect=fake_exec)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session
