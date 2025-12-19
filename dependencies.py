from typing import Annotated

from fastapi import Depends, Request
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.exceptions.auth import (
    InvalidJWTTokenError,
    InvalidTokenHTTPError,
    NoAccessTokenHTTPError,
)
from app.services.auth import AuthService
from sqlalchemy.orm import Session


class PaginationParams(BaseModel):
    page: int | None = Field(default=1, ge=1)
    per_page: int | None = Field(default=10, ge=1, le=100)


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    """Получение токена из заголовка Authorization или cookies"""
    # Сначала пробуем получить из заголовка
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    
    # Если нет в заголовке, пробуем из cookies
    token = request.cookies.get("access_token", None)
    if token is None:
        raise NoAccessTokenHTTPError
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    """Получение ID текущего пользователя из токена"""
    try:
        data = AuthService.decode_token(token)
    except InvalidJWTTokenError:
        raise InvalidTokenHTTPError
    return data["user_id"]


def get_current_user_role(token: str = Depends(get_token)) -> str:
    """Получение роли текущего пользователя из токена"""
    try:
        data = AuthService.decode_token(token)
    except InvalidJWTTokenError:
        raise InvalidTokenHTTPError
    return data.get("role", "volunteer")


UserIdDep = Annotated[int, Depends(get_current_user_id)]
UserRoleDep = Annotated[str, Depends(get_current_user_role)]
DBDep = Annotated[Session, Depends(get_db)]


def is_admin(role: str = Depends(get_current_user_role)) -> bool:
    """Проверка, является ли пользователь администратором"""
    return role == "admin"


IsAdminDep = Annotated[bool, Depends(is_admin)]
