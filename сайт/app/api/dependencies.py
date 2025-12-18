from typing import Annotated, Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.exceptions import InvalidJWTTokenError, IsNotAdminHTTPError, NoAccessTokenHTTPError
from app.models import UserModel


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    """
    Извлекаем user_id из JWT-токена.
    Аналогично тому, как это делается в учебных примерах с get_current_user_id().
    """
    if not token:
        raise NoAccessTokenHTTPError()

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise InvalidJWTTokenError()
        return int(user_id)
    except JWTError:
        raise InvalidJWTTokenError()


UserIdDep = Annotated[int, Depends(get_current_user_id)]
DBDep = Annotated[Session, Depends(get_db)]


async def check_is_admin(db: DBDep, user_id: UserIdDep):
    """
    Пример из задания:

    app/api/dependencies.py
    async def check_is_admin(db: DBDep, user_id:UserIdDep):
        user = await db.users.get_one_or_none_with_role(id=user_id)
        if user.role.name == "admin":
            return True
        else:
            raise IsNotAdminHTTPError
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user and user.role and user.role.name == "admin":
        return True
    raise IsNotAdminHTTPError()


IsAdminDep = Annotated[bool, Depends(check_is_admin)]

from typing import Annotated

from fastapi import Depends

from app.exceptions import IsNotAdminHTTPError


class Role:
    def __init__(self, name: str):
        self.name = name


class User:
    def __init__(self, id: int, name: str, role: Role):
        self.id = id
        self.name = name
        self.role = role


class FakeUserRepo:
    """
    Упрощённый репозиторий пользователей.
    Вместо БД используем память, но интерфейс похож на пример.
    """

    def __init__(self):
        admin_role = Role("admin")
        user_role = Role("user")
        self._users: dict[int, User] = {
            1: User(1, "Admin", admin_role),
            2: User(2, "Volunteer", user_role),
        }

    async def get_one_or_none_with_role(self, id: int) -> User | None:
        return self._users.get(id)


class FakeDB:
    def __init__(self):
        self.users = FakeUserRepo()


async def get_db() -> FakeDB:
    """
    Аналог DBDep из примера.
    """
    return FakeDB()


DBDep = Annotated[FakeDB, Depends(get_db)]


async def get_current_user_id() -> int:
    """
    Упрощённо считаем, что всегда авторизован админ с id=1.

    В полноценном проекте здесь должна быть логика разбора JWT-токена:

    SECRET_KEY=...
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=60
    DB_NAME=test.db
    """

    return 1


UserIdDep = Annotated[int, Depends(get_current_user_id)]


async def check_is_admin(db: DBDep, user_id: UserIdDep):
    """
    Вариант из задания:

    app/api/dependencies.py
    async def check_is_admin(db: DBDep, user_id:UserIdDep):
        user = await db.users.get_one_or_none_with_role(id=user_id)
        if user.role.name == "admin":
            return True
        else:
            raise IsNotAdminHTTPError
    """
    user = await db.users.get_one_or_none_with_role(id=user_id)
    if user and user.role.name == "admin":
        return True
    raise IsNotAdminHTTPError


IsAdminDep = Annotated[bool, Depends(check_is_admin)]



