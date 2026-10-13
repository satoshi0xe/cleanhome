"""Import central des modèles pour qu'ils soient enregistrés par SQLAlchemy."""
from app.models.user import User
from app.models.service import Service
from app.models.booking import Booking

__all__ = ["User", "Service", "Booking"]