from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SEventAddRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    ngo_id: int
    scheduled_at: datetime
    location: Optional[str] = Field(None, max_length=200)
    max_volunteers: Optional[int] = Field(None, ge=1)
    duration_hours: int = Field(default=2, ge=1, le=24)


class SEventAdd(BaseModel):
    title: str
    description: Optional[str] = None
    ngo_id: int
    scheduled_at: datetime
    location: Optional[str] = None
    max_volunteers: Optional[int] = None
    duration_hours: int = 2
    status: str = "active"


class SEventGet(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    ngo_id: int
    scheduled_at: datetime
    location: Optional[str] = None
    max_volunteers: Optional[int] = None
    duration_hours: int = 2
    status: str = "active"

    class Config:
        from_attributes = True


class SEventPatch(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    max_volunteers: Optional[int] = Field(None, ge=1)
    status: Optional[str] = None

