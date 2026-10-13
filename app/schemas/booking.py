from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.service import ServiceOut
from app.schemas.user import UserOut

BookingStatus = Literal["pending", "confirmed", "done", "cancelled"]


class BookingCreate(BaseModel):
    service_id: int
    date: date
    address: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=30)


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    service_id: int
    date: date
    address: str
    phone: str
    price: int
    status: BookingStatus
    created_at: datetime | None = None
    user: UserOut | None = None
    service: ServiceOut | None = None
