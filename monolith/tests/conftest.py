import os

# Use an isolated on-disk SQLite database for tests. Must be set before the app
# (and its database engine) are imported.
os.environ.setdefault("DATABASE_URL", "sqlite:///./_pytest.db")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    # Start from a clean schema for the test session.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)
