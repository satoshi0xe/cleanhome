from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_user
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["api:bookings"])


@router.get("/me", response_model=list[BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    return BookingService(db).list_for_user(user.id)


@router.post("/", response_model=BookingOut, status_code=201)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    return BookingService(db).create(
        user=user,
        service_id=data.service_id,
        booking_date=data.date,
        address=data.address,
        phone=data.phone,
    )
