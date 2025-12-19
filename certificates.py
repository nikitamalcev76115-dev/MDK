from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SCertificateGet(BaseModel):
    id: int
    volunteer_id: int
    title: str
    description: Optional[str] = None
    hours_required: int = 0
    issued_at: datetime

    class Config:
        from_attributes = True

