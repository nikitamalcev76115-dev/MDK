from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, EmailStr, Field

if TYPE_CHECKING:
    from app.schemes.roles import SRoleGet


class SUserAddRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role_id: Optional[int] = None
    city: Optional[str] = Field(None, max_length=100)


class SUserAdd(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    role_id: int
    city: Optional[str] = None


class SUserAuth(BaseModel):
    email: EmailStr
    password: str


class SUserGet(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int
    total_hours: int = 0
    rating: float = 0.0
    city: Optional[str] = None


class SUserGetWithRels(SUserGet):
    role: "SRoleGet"

    class Config:
        from_attributes = True


class SUserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    city: Optional[str] = Field(None, max_length=100)

