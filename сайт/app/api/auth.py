from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import DBDep
from app.core.config import get_settings
from app.models import UserCreate, UserPublic, UserModel, RoleModel


router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", summary="Регистрация волонтёра", response_model=UserPublic)
async def register_user(data: UserCreate, db: DBDep):
    """
    Пример использования JSON body как в присланных фрагментах JS:

    try {
      const response = await fetch(AUTH_ENDPOINTS.REGISTER, {
        method: 'POST',
        headers: { 'accept': 'application/json','Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });
    }
    """
    existing = db.query(UserModel).filter(UserModel.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    # В учебных целях пароль не хэшируем, но поле называется hashed_password
    volunteer_role = db.query(RoleModel).filter(RoleModel.name == "volunteer").first()
    if not volunteer_role:
        raise HTTPException(status_code=500, detail="Роль volunteer не найдена в базе")

    user = UserModel(
        name=data.name,
        email=data.email,
        hashed_password=data.password,
        role_id=volunteer_role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserPublic.from_orm(user)


@router.post("/login", summary="Логин и получение JWT-токена", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DBDep):
    """
    Стандартный endpoint tokenUrl для OAuth2PasswordBearer.
    """
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or user.hashed_password != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")

    settings = get_settings()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return Token(access_token=token)

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr


router = APIRouter(tags=["Авторизация"])


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


fake_users: list[RegisterResponse] = []


@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="Регистрация волонтёра (пример из fetch)",
)
async def register_user(data: RegisterRequest):
    """
    Реализация под пример:

    try {
      const response = await fetch(AUTH_ENDPOINTS.REGISTER, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: name,
          email: email,
          password: password
        })
      });
      const data = await response.json();
      console.log(data)
    }
    """
    new_id = len(fake_users) + 1
    user = RegisterResponse(id=new_id, name=data.name, email=data.email)
    fake_users.append(user)
    return user



