"""
In-memory база данных для работы без реального MySQL подключения.
Используется SQLite в памяти для имитации работы БД.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# SQLite в памяти - работает без файлов и настроек
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Получение сессии БД (in-memory SQLite)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_mock_database():
    """Инициализация in-memory базы данных с начальными данными"""
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
        print(f"Ошибка при инициализации: {e}")
        db.rollback()
    finally:
        db.close()

