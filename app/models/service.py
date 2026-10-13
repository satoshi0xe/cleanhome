from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    category = Column(String(80), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)          # en FCFA
    duration = Column(String(50), nullable=False)    # ex: "3 heures"
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())