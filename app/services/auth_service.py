from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    """Logique métier authentification (inscription / connexion)."""

    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def login(self, email: str, password: str) -> tuple[str, User]:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants invalides",
            )
        token = create_access_token(
            {"sub": str(user.id), "is_admin": user.is_admin}
        )
        return token, user

    def register(self, data: UserCreate) -> tuple[str, User]:
        if self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un compte existe déjà avec cet e-mail",
            )
        user = self.repo.create(
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            hashed_password=hash_password(data.password),
        )
        token = create_access_token(
            {"sub": str(user.id), "is_admin": user.is_admin}
        )
        return token, user

    def ensure_admin(
        self,
        *,
        email: str,
        password: str,
        full_name: str = "Admin CleanHome",
        phone: str = "0700000000",
    ) -> User:
        """Crée un admin s'il n'existe pas encore (dev)."""
        existing = self.repo.get_by_email(email)
        if existing:
            return existing
        return self.repo.create(
            full_name=full_name,
            email=email,
            phone=phone,
            hashed_password=hash_password(password),
            is_admin=True,
        )
