from typing import List

from fastapi import APIRouter, HTTPException

from app.api.dependencies import IsAdminDep, UserIdDep, DBDep
from app.models import (
    EventCreate,
    EventPublic,
    Registration,
    Certificate,
    EventModel,
    RegistrationModel,
    UserModel,
    CertificateModel,
)


router = APIRouter()


@router.get("/", summary="Список волонтёрских мероприятий", response_model=List[EventPublic])
async def list_events(db: DBDep):
    events = db.query(EventModel).all()
    result: List[EventPublic] = []
    for e in events:
        volunteers_count = len(e.registrations)
        result.append(
            EventPublic(
                id=e.id,
                title=e.title,
                description=e.description,
                ngo_id=e.ngo_id,
                scheduled_at=e.scheduled_at,
                duration_hours=e.duration_hours,
                volunteers_count=volunteers_count,
            )
        )
    return result


@router.post("/", summary="Создать мероприятие (admin)", response_model=EventPublic)
async def create_event(data: EventCreate, db: DBDep, is_admin: IsAdminDep):
    event = EventModel(
        title=data.title,
        description=data.description,
        ngo_id=data.ngo_id,
        scheduled_at=data.scheduled_at,
        duration_hours=data.duration_hours,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return EventPublic(
        id=event.id,
        title=event.title,
        description=event.description,
        ngo_id=event.ngo_id,
        scheduled_at=event.scheduled_at,
        duration_hours=event.duration_hours,
        volunteers_count=0,
    )


@router.post("/{event_id}/signup", summary="Записаться на мероприятие", response_model=Registration)
async def signup_for_event(event_id: int, user_id: UserIdDep, db: DBDep):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    existing = (
        db.query(RegistrationModel)
        .filter(
            RegistrationModel.event_id == event_id,
            RegistrationModel.volunteer_id == user_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже записаны на это мероприятие")

    reg = RegistrationModel(event_id=event_id, volunteer_id=user_id)
    db.add(reg)
    db.commit()
    db.refresh(reg)

    return Registration.from_orm(reg)


@router.post("/{event_id}/complete", summary="Отметить мероприятие как завершённое (admin)")
async def complete_event(event_id: int, db: DBDep, is_admin: IsAdminDep):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")

    regs = db.query(RegistrationModel).filter(RegistrationModel.event_id == event_id).all()
    for reg in regs:
        reg.hours_earned = event.duration_hours
        user = db.query(UserModel).filter(UserModel.id == reg.volunteer_id).first()
        if user:
            user.total_hours += event.duration_hours
            user.rating = float(user.total_hours)

    db.commit()
    return {"msg": "Мероприятие завершено, часы волонтёров начислены"}


@router.post("/certificates/{volunteer_id}", summary="Выдать сертификат волонтёру (admin)", response_model=Certificate)
async def issue_certificate(volunteer_id: int, db: DBDep, is_admin: IsAdminDep):
    user = db.query(UserModel).filter(UserModel.id == volunteer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    text = f"Сертификат участия: {user.name} — {user.total_hours} часов волонтёрской деятельности."

    cert = CertificateModel(
        volunteer_id=volunteer_id,
        text=text,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    return Certificate.from_orm(cert)

from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(tags=["Мероприятия"])


class EventCreate(BaseModel):
    title: str
    description: str | None = None
    ngo_name: str
    start_at: datetime | None = None
    hours: int = 2


class Event(BaseModel):
    id: int
    title: str
    description: str | None = None
    ngo_name: str
    start_at: datetime | None = None
    hours: int


_events: list[Event] = []


@router.get("/events", summary="Список волонтёрских мероприятий", response_model=List[Event])
async def list_events():
    return _events


@router.post("/ngo/events", summary="Создать мероприятие НКО", response_model=Event)
async def create_event(data: EventCreate):
    """
    НКО публикует волонтёрское мероприятие.
    """
    new_id = len(_events) + 1
    event = Event(id=new_id, **data.model_dict())
    _events.append(event)
    return event


@router.get("/events/{event_id}", summary="Информация о мероприятии", response_model=Event)
async def get_event(event_id: int):
    for e in _events:
        if e.id == event_id:
            return e
    raise HTTPException(status_code=404, detail="Мероприятие не найдено")



