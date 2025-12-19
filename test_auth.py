import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from main import app

# Тестовая база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def setup_database():
    """Создание и удаление тестовой БД для каждого теста"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_register_user_success(setup_database):
    """Тест успешной регистрации пользователя"""
    response = client.post(
        "/auth/register",
        json={
            "name": "Тестовый Пользователь",
            "email": "test@example.com",
            "password": "testpass123",
            "city": "Москва"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_register_user_duplicate_email(setup_database):
    """Тест регистрации с существующим email"""
    # Первая регистрация
    client.post(
        "/auth/register",
        json={
            "name": "Первый Пользователь",
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )
    
    # Попытка зарегистрироваться с тем же email
    response = client.post(
        "/auth/register",
        json={
            "name": "Второй Пользователь",
            "email": "duplicate@example.com",
            "password": "password456"
        }
    )
    assert response.status_code == 409
    assert "уже существует" in response.json()["detail"]


def test_register_user_invalid_email(setup_database):
    """Тест регистрации с невалидным email"""
    response = client.post(
        "/auth/register",
        json={
            "name": "Тест",
            "email": "invalid-email",
            "password": "password123"
        }
    )
    assert response.status_code == 422  # Validation error


def test_register_user_short_password(setup_database):
    """Тест регистрации с коротким паролем"""
    response = client.post(
        "/auth/register",
        json={
            "name": "Тест",
            "email": "test@example.com",
            "password": "12345"  # Меньше 6 символов
        }
    )
    assert response.status_code == 422  # Validation error


def test_login_success(setup_database):
    """Тест успешного входа"""
    # Сначала регистрируем пользователя
    client.post(
        "/auth/register",
        json={
            "name": "Тестовый Пользователь",
            "email": "login@example.com",
            "password": "testpass123"
        }
    )
    
    # Пытаемся войти
    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(setup_database):
    """Тест входа с неверными данными"""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_me_without_token(setup_database):
    """Тест получения профиля без токена"""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_me_with_token(setup_database):
    """Тест получения профиля с валидным токеном"""
    # Регистрация
    client.post(
        "/auth/register",
        json={
            "name": "Профиль Тест",
            "email": "profile@example.com",
            "password": "testpass123"
        }
    )
    
    # Вход
    login_response = client.post(
        "/auth/login",
        json={
            "email": "profile@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Получение профиля
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "profile@example.com"

