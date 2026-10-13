from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    name: str = Field(..., max_length=120)
    category: str = Field(..., max_length=80)
    description: str
    price: int = Field(..., gt=0)
    duration: str = Field(..., max_length=50)
    image_url: str | None = Field(default=None, max_length=500)


class ServiceUpdate(ServiceCreate):
    """Même champs que la création ; image_url omise = image conservée."""
    pass


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    description: str
    price: int
    duration: str
    image_url: str | None
    created_at: datetime | None = None
