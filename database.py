from typing import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import get_settings

Base = declarative_base()

# Проверяем, нужно ли использовать in-memory БД
USE_MOCK_DB = os.getenv("USE_MOCK_DB", "true").lower() == "true"

if USE_MOCK_DB:
    # Используем SQLite в памяти - работает без настройки MySQL
    DATABASE_URL = "sqlite:///:memory:"
    print("📦 Используется in-memory база данных (SQLite)")
    print("   Для использования MySQL установите USE_MOCK_DB=false в .env")
else:
    # Реальное подключение к MySQL
    settings = get_settings()
    DATABASE_URL = (
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASS}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
    )
    print("📦 Используется MySQL база данных")

if USE_MOCK_DB:
    # Используем SQLite в памяти - работает без настройки MySQL
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # Реальное подключение к MySQL
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    except Exception as e:
        print(f"⚠️ Ошибка подключения к MySQL: {e}")
        print("   Переключаюсь на in-memory БД (SQLite)")
        DATABASE_URL = "sqlite:///:memory:"
        USE_MOCK_DB = True
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Получение сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Инициализация базы данных с начальными данными"""
    from sqlalchemy.orm import Session
    from app.models import RoleModel, NGOModel, EventModel
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    
    db = Session(engine)
    try:
        # Создаем роли, если их нет
        if db.query(RoleModel).count() == 0:
            roles = [
                RoleModel(name="admin"),
                RoleModel(name="coordinator"),
                RoleModel(name="volunteer"),
            ]
            db.add_all(roles)
            db.commit()
            print("✓ Созданы роли: admin, coordinator, volunteer")
        
        # Создаем примеры НКО
        if db.query(NGOModel).count() == 0:
            ngos = [
                NGOModel(name="НКО «Город добрых дел»", description="Организация занимается проведением благотворительных мероприятий."),
                NGOModel(name="НКО «Поддержка рядом»", description="Онлайн поддержка и консультации."),
                NGOModel(name="НКО «Чистый город»", description="Экологические инициативы и субботники."),
            ]
            db.add_all(ngos)
            db.commit()
            print("✓ Созданы примеры НКО")
        
        # Создаем примеры мероприятий
        from datetime import datetime, timedelta
        if db.query(EventModel).count() == 0:
            events = [
                EventModel(
                    title="Помощь в проведении благотворительного марафона",
                    description="Регистрация участников, навигация по площадке, помощь организаторам.",
                    ngo_id=1,
                    scheduled_at=datetime.now() + timedelta(days=30),
                    location="Москва, ВДНХ",
                    max_volunteers=30,
                    duration_hours=8,
                    status="active"
                ),
                EventModel(
                    title="Онлайн‑поддержка горячей линии НКО",
                    description="Консультации по стандартным вопросам, помощь в навигации.",
                    ngo_id=2,
                    scheduled_at=datetime.now() + timedelta(days=15),
                    location="Онлайн",
                    max_volunteers=20,
                    duration_hours=4,
                    status="active"
                ),
                EventModel(
                    title="Экологический субботник в парке",
                    description="Уборка территории, посадка деревьев, организация экологических квестов.",
                    ngo_id=3,
                    scheduled_at=datetime.now() + timedelta(days=45),
                    location="Москва, Сокольники",
                    max_volunteers=50,
                    duration_hours=5,
                    status="active"
                ),
            ]
            db.add_all(events)
            db.commit()
            print("✓ Созданы примеры мероприятий")
            
    except Exception as e:
        print(f"⚠️ Ошибка при инициализации: {e}")
        db.rollback()
    finally:
        db.close()


