from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


#
# SQLAlchemy-модели (таблицы)
#


class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("UserModel", back_populates="role")


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    total_hours = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    role = relationship("RoleModel", back_populates="users")
    registrations = relationship("RegistrationModel", back_populates="volunteer")


class NGOModel(Base):
    __tablename__ = "ngos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)


class EventModel(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    duration_hours = Column(Integer, default=2)

    registrations = relationship("RegistrationModel", back_populates="event")


class RegistrationModel(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    hours_earned = Column(Integer, default=0)

    event = relationship("EventModel", back_populates="registrations")
    volunteer = relationship("UserModel", back_populates="registrations")


class CertificateModel(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    volunteer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)


#
# Pydantic-схемы (для запросов/ответов)
#


class Role(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: int
    role: Role
    total_hours: int
    rating: float

    class Config:
        orm_mode = True


class NGO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    ngo_id: int
    scheduled_at: datetime
    duration_hours: int = 2


class EventCreate(EventBase):
    pass


class EventPublic(EventBase):
    id: int
    volunteers_count: int

    class Config:
        orm_mode = True


class Registration(BaseModel):
    id: int
    event_id: int
    volunteer_id: int
    registered_at: datetime
    hours_earned: int = 0

    class Config:
        orm_mode = True


class Certificate(BaseModel):
    id: int
    volunteer_id: int
    text: str
    issued_at: datetime

    class Config:
        orm_mode = True



