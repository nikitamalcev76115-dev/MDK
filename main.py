from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.database import Base, engine
from app.api.auth import router as auth_router
from app.api.roles import router as roles_router
from app.api.events import router as events_router


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


@app.on_event("startup")
async def on_startup() -> None:
    """
    Инициализация базы данных и создание начальных данных.
    """
    from app.core.database import init_database
    init_database()
    print("✅ База данных инициализирована и готова к работе!")


# Статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", tags=["Главная"])
async def home():
    """
    Главная страница - возвращает HTML файл
    """
    return FileResponse("app/static/index.html")


@app.get("/api", tags=["API"])
async def api_info():
    return {
        "project": "RukaPomoshchi",
        "description": "Система управления волонтерскими проектами. НКО публикуют мероприятия, волонтеры записываются, ведется учет часов, рейтинги и сертификаты.",
    }


# API роутеры
app.include_router(auth_router, tags=["Аутентификация"])
app.include_router(roles_router, prefix="/api/roles", tags=["Роли"])
app.include_router(events_router, prefix="/api/events", tags=["Мероприятия"])
