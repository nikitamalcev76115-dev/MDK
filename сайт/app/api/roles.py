from typing import List

from fastapi import APIRouter

from app.api.dependencies import IsAdminDep, DBDep
from app.models import Role, RoleModel


router = APIRouter()


@router.get("/", summary="Получение списка ролей")
async def get_all_roles(db: DBDep, is_admin: IsAdminDep) -> List[Role]:
    """
    Разграничение прав пользователей.

    Пример из задания:

    app/api/roles.py
    @router.get("/roles", summary="Получение списка ролей")
    async def get_all_roles(
        db: DBDep,
        is_admin: IsAdminDep,# добавили это
    ) -> list[SRoleGet]:
        return await RoleService(db).get_roles()
    """
    roles = db.query(RoleModel).all()
    return [Role.from_orm(r) for r in roles]

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import DBDep, IsAdminDep


router = APIRouter(tags=["Роли"])


class SRoleGet(BaseModel):
    id: int
    name: str


class RoleService:
    """
    Сервис для работы с ролями, как в примере из задания.
    """

    def __init__(self, db: DBDep):
        self.db = db

    async def get_roles(self) -> list[SRoleGet]:
        # В реальном приложении — запрос к БД.
        roles = [
            SRoleGet(id=1, name="admin"),
            SRoleGet(id=2, name="user"),
            SRoleGet(id=3, name="ngo"),
            SRoleGet(id=4, name="volunteer"),
        ]
        return roles


DBDepAnnotated = Annotated[DBDep, Depends(lambda db: db)]


@router.get("/roles", summary="Получение списка ролей")
async def get_all_roles(
    db: DBDepAnnotated,
    is_admin: IsAdminDep,  # Разграничение прав пользователей
) -> list[SRoleGet]:
    """
    Пример из задания:

    @router.get("/roles", summary="Получение списка ролей")
    async def get_all_roles(
        db: DBDep,
        is_admin: IsAdminDep,# добавили это
    ) -> list[SRoleGet]:
        return await RoleService(db).get_roles()
    """
    return await RoleService(db).get_roles()



