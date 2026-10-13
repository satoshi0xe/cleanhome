from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Accès BDD pour les utilisateurs."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def create(
        self,
        full_name: str,
        email: str,
        phone: str,
        hashed_password: str,
        is_admin: bool = False,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            hashed_password=hashed_password,
            is_admin=is_admin,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
