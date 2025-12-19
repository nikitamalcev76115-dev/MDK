from datetime import datetime, timezone, timedelta

from app.core.config import get_settings
from app.exceptions.auth import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidPasswordError,
    InvalidJWTTokenError,
    JWTTokenExpiredError,
)
from app.exceptions.base import ObjectAlreadyExistsError
from app.schemes.users import (
    SUserAdd,
    SUserAddRequest,
    SUserAuth,
)
from app.schemes.relations_users_roles import SUserGetWithRels
from app.services.base import BaseService
from app.repositories.users import UsersRepository
from app.repositories.roles import RolesRepository
import jwt
from passlib.context import CryptContext


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        settings = get_settings()
        to_encode = data.copy()
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, plain_password) -> str:
        return cls.pwd_context.hash(plain_password)

    @classmethod
    def decode_token(cls, token: str) -> dict:
        settings = get_settings()
        try:
            return jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM])
        except jwt.exceptions.DecodeError as ex:
            raise InvalidJWTTokenError from ex
        except jwt.exceptions.ExpiredSignatureError as ex:
            raise JWTTokenExpiredError from ex

    def register_user(self, user_data: SUserAddRequest):
        users_repo = UsersRepository(self.db)
        roles_repo = RolesRepository(self.db)
        
        # Проверка существующего пользователя
        existing = users_repo.get_one_or_none(email=user_data.email)
        if existing:
            raise UserAlreadyExistsError
        
        # Получение роли по умолчанию (volunteer)
        if user_data.role_id is None:
            volunteer_role = roles_repo.get_one_or_none(name="volunteer")
            if not volunteer_role:
                raise ValueError("Роль volunteer не найдена в базе")
            role_id = volunteer_role.id
        else:
            role_id = user_data.role_id

        try:
            hashed_password: str = self.hash_password(user_data.password)
            new_user_data = SUserAdd(
                email=user_data.email,
                hashed_password=hashed_password,
                name=user_data.name,
                role_id=role_id,
                city=user_data.city,
            )
            return users_repo.add(new_user_data)
        except ObjectAlreadyExistsError:
            raise UserAlreadyExistsError

    def login_user(self, user_data: SUserAuth):
        users_repo = UsersRepository(self.db)
        user = users_repo.get_one_or_none_with_role(email=user_data.email)
        if not user:
            raise UserNotFoundError
        if not self.verify_password(user_data.password, user.hashed_password):
            raise InvalidPasswordError
        access_token: str = self.create_access_token(
            {
                "user_id": user.id,
                "role": user.role.name,
            }
        )
        return access_token

    def get_me(self, user_id: int):
        from app.models import RegistrationModel, CertificateModel, EventModel
        from app.schemes.registrations import SRegistrationWithEvent
        from app.schemes.certificates import SCertificateGet
        
        users_repo = UsersRepository(self.db)
        user: SUserGetWithRels | None = users_repo.get_one_or_none_with_role(
            id=user_id
        )
        if not user:
            raise UserNotFoundError
        
        # Получаем регистрации пользователя
        registrations = self.db.query(RegistrationModel).filter(
            RegistrationModel.volunteer_id == user_id
        ).all()
        
        user_registrations = []
        for reg in registrations:
            event = self.db.query(EventModel).filter(EventModel.id == reg.event_id).first()
            reg_data = SRegistrationWithEvent(
                id=reg.id,
                event_id=reg.event_id,
                volunteer_id=reg.volunteer_id,
                registered_at=reg.registered_at,
                hours_earned=reg.hours_earned,
                status=reg.status,
                event_title=event.title if event else None,
                scheduled_at=event.scheduled_at if event else None,
                location=event.location if event else None,
            )
            user_registrations.append(reg_data)
        
        # Получаем сертификаты пользователя
        certificates = self.db.query(CertificateModel).filter(
            CertificateModel.volunteer_id == user_id
        ).all()
        
        user_certificates = [
            SCertificateGet.model_validate(cert, from_attributes=True)
            for cert in certificates
        ]
        
        # Добавляем данные в объект пользователя
        user_dict = user.model_dump()
        user_dict['registrations'] = [r.model_dump() for r in user_registrations]
        user_dict['certificates'] = [c.model_dump() for c in user_certificates]
        
        return SUserGetWithRels(**user_dict)

