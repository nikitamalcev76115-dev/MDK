from fastapi import HTTPException


class MyAppHTTPError(HTTPException):
    """Базовое HTTP-исключение приложения."""


class InvalidJWTTokenError(MyAppHTTPError):
    status_code = 401
    detail = "Неверный JWT-токен"


class InvalidTokenHTTPError(MyAppHTTPError):
    status_code = 401
    detail = "Неверный токен"


class NoAccessTokenHTTPError(MyAppHTTPError):
    status_code = 401
    detail = "Токен доступа не передан"


class IsNotAdminHTTPError(MyAppHTTPError):
    status_code = 403
    detail = "Недостаточно прав"

from .auth import IsNotAdminHTTPError

__all__ = ["IsNotAdminHTTPError"]



