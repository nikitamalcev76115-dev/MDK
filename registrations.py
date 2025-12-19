from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SRegistrationGet(BaseModel):
    id: int
    event_id: int
    volunteer_id: int
    registered_at: datetime
    hours_earned: int = 0
    status: str = "registered"

    class Config:
        from_attributes = True


class SRegistrationWithEvent(SRegistrationGet):
    event_title: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    location: Optional[str] = None

