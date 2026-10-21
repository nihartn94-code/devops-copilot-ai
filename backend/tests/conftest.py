import asyncio
import pytest
from backend.app.database import init_db

@pytest.fixture(autouse=True, scope="session")
def setup_database():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())
    yield
    loop.close()
