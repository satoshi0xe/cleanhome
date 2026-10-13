from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.user import User
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import BookingStatus
from app.services.service_service import ServiceService

ALLOWED_STATUSES = {"pending", "confirmed", "done", "cancelled"}


class BookingService:
    """Logique métier des réservations."""

    def __init__(self, db: Session):
        self.repo = BookingRepository(db)
        self.services = ServiceService(db)

    def list_all(self) -> list[Booking]:
        return self.repo.list_all()

    def list_for_user(self, user_id: int) -> list[Booking]:
        return self.repo.list_for_user(user_id)

    def get_by_id(self, booking_id: int) -> Booking:
        booking = self.repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Réservation introuvable",
            )
        return booking

    def get_for_user(self, booking_id: int, user: User) -> Booking:
        booking = self.get_by_id(booking_id)
        if booking.user_id != user.id and not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Réservation introuvable",
            )
        return booking

    def create(
        self,
        *,
        user: User,
        service_id: int,
        booking_date: date,
        address: str,
        phone: str,
    ) -> Booking:
        if booking_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date d'intervention doit être aujourd'hui ou plus tard",
            )
        if not address.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'adresse est obligatoire",
            )
        if not phone.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le téléphone est obligatoire",
            )

        service = self.services.get_by_id(service_id)
        return self.repo.create(
            user_id=user.id,
            service_id=service.id,
            booking_date=booking_date,
            address=address.strip(),
            phone=phone.strip(),
            price=service.price,
        )

    def update_status(self, booking_id: int, new_status: BookingStatus) -> Booking:
        if new_status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Statut non autorisé",
            )
        booking = self.get_by_id(booking_id)
        return self.repo.update_status(booking, new_status)
