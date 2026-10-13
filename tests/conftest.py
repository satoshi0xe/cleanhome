from __future__ import annotations

import os

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_cleanhome.db"
os.environ["JWT_SECRET"] = "test-secret"

from collections.abc import Generator
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.service import Service
from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.fixture(autouse=True)
def reset_db() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def service(db: Session) -> Service:
    item = Service(
        name="Ménage standard 2 pièces",
        category="Ménage standard",
        description="Nettoyage complet d'un appartement 2 pièces.",
        price=15000,
        duration="3 heures",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def client_user(db: Session) -> User:
    return UserRepository(db).create(
        full_name="Awa Traore",
        email="awa@test.ci",
        phone="0700112233",
        hashed_password=hash_password("secret12"),
    )


@pytest.fixture
def admin_user(db: Session) -> User:
    return UserRepository(db).create(
        full_name="Admin CleanHome",
        email="admin@cleanhome.ci",
        phone="0700000000",
        hashed_password=hash_password("admin123"),
        is_admin=True,
    )


def login(client: TestClient, email: str, password: str) -> None:
    response = client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )
    assert response.status_code == 303


def tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()
