from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=False)
    price = Column(Integer, nullable=False)          # snapshot du prix au moment de la résa
    status = Column(String(20), default="pending", nullable=False)  # pending|confirmed|done|cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", lazy="joined")
    service = relationship("Service", lazy="joined")