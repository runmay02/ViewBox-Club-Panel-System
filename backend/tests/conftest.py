import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.source import AcquisitionSource
from app.models.user import User


@pytest.fixture
def api(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestingSession() as db:
        db.add_all([
            AcquisitionSource(name="Website", channel_type="WEBSITE", code="website-organic", is_active=True),
            AcquisitionSource(name="Instagram", channel_type="INSTAGRAM", code="instagram-organic", is_active=True),
            AcquisitionSource(name="Meta Ads", channel_type="META_ADS", code="meta-leadgen-ads", is_active=True),
            User(phone="9999900001", role="ADMIN", is_active=True),
            User(phone="9999900002", role="OPERATIONS", is_active=True),
        ])
        db.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app, follow_redirects=False)
    yield client, TestingSession
    app.dependency_overrides.clear()
    engine.dispose()
