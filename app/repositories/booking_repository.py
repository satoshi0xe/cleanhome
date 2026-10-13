from datetime import date

from sqlalchemy.orm import Session

from app.models.booking import Booking


class BookingRepository:
    """Accès BDD pour les réservations."""

    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Booking]:
        return (
            self.db.query(Booking)
            .order_by(Booking.created_at.desc())
            .all()
        )

    def list_for_user(self, user_id: int) -> list[Booking]:
        return (
            self.db.query(Booking)
            .filter(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
            .all()
        )

    def get_by_id(self, booking_id: int) -> Booking | None:
        return self.db.get(Booking, booking_id)

    def create(
        self,
        *,
        user_id: int,
        service_id: int,
        booking_date: date,
        address: str,
        phone: str,
        price: int,
    ) -> Booking:
        booking = Booking(
            user_id=user_id,
            service_id=service_id,
            date=booking_date,
            address=address,
            phone=phone,
            price=price,
            status="pending",
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_status(self, booking: Booking, status: str) -> Booking:
        booking.status = status
        self.db.commit()
        self.db.refresh(booking)
        return booking
