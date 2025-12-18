from fastapi import FastAPI

from app.core.database import Base, engine
from app.api.auth import router as auth_router
from app.api.roles import router as roles_router
from app.api.events import router as events_router


app = FastAPI(
    title="RukaPomoshchi",
    version="0.1.0",
    description=(
        "Система управления волонтерскими проектами «РукаПомощи». "
        "НКО публикуют мероприятия, волонтеры записываются на события, "
        "ведётся учет часов, рейтинга и выдача сертификатов."
    ),
)


@app.on_event("startup")
async def on_startup() -> None:
    """
    Создание таблиц и начальных данных (роли, админ).
    """
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Главная"])
async def home():
    return {"data": "Добро пожаловать в систему «РукаПомощи»"}


app.include_router(auth_router, prefix="/auth", tags=["Аутентификация"])
app.include_router(roles_router, prefix="/roles", tags=["Роли"])
app.include_router(events_router, prefix="/events", tags=["Мероприятия"])

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.shop import router as shop_router
from app.api.roles import router as roles_router
from app.api.auth import router as auth_router
from app.api.trips import router as trips_router
from app.api.events import router as events_router
from app.api.volunteers import router as volunteers_router


app = FastAPI(
    title="RukaPomoshchi",
    version="0.2.0",
    description="Система управления волонтерскими проектами «РукаПомощи»",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Главная"])
async def home():
    return {
        "project": "RukaPomoshchi",
        "description": "Система управления волонтерскими проектами. НКО публикуют мероприятия, волонтеры записываются, ведется учет часов, рейтинги и сертификаты.",
    }


app.include_router(shop_router, prefix="/shop")
app.include_router(roles_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
app.include_router(trips_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(volunteers_router, prefix="/api")


