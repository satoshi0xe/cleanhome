"""Données de démarrage pour l'environnement de développement."""

import logging

from app.config import settings
from app.database import SessionLocal
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

DEV_ADMIN_EMAIL = "admin@cleanhome.ci"
DEV_ADMIN_PASSWORD = "admin123"


def seed_dev_admin() -> None:
    """Crée un compte admin de démo si absent (uniquement en development)."""
    if settings.APP_ENV != "development":
        return

    db = SessionLocal()
    try:
        user = AuthService(db).ensure_admin(
            email=DEV_ADMIN_EMAIL,
            password=DEV_ADMIN_PASSWORD,
        )
        logger.info("Admin prêt : %s (id=%s)", user.email, user.id)
    finally:
        db.close()
