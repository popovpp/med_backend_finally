import jwt
from fastapi import HTTPException
from sqlalchemy.future import select as async_select
from datetime import datetime
from passlib.context import CryptContext

from core.config.db import get_session
from core.config.settings import SECRET_KEY
from core.sa_tables.accounts import UserTable, AdminUserTable


class Auth():
    """Класс, реализующий методы верификации пароля, кодирования и декодирования jwt-токена"""

    secret = SECRET_KEY
    hasher = CryptContext(schemes=['bcrypt'])

    async def verify_password(self, password, password_hash):
        """Верификация пароля"""

        return self.hasher.verify(password, password_hash)

    async def encode_token(self, login, password):
        """Кодирование access токена"""
        payload = {
            'iat' : datetime.utcnow(),
            'sub' : {
                        "login": login,
                        "password": password
                    }
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    async def decode_token(self, token):
        """Декодирование access токена"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload.get('sub'):
                return payload['sub']
            return None
        except jwt.InvalidTokenError:
            return None


    # Авторизация через полученный ранее токен
    async def token_auth(self, auth_token: str) -> UserTable:

        payload = await self.decode_token(auth_token)

        if payload:

            async with get_session() as s:
                sql = async_select(UserTable).filter(UserTable.login_phone_number == payload['login'],
                                                     UserTable.is_active)
                user = (await s.execute(sql)).unique().scalars().one_or_none()

                if not user:
                    raise HTTPException(status_code=404, detail=f'Активный пользователь {user.email} не найден')
                try:
                    is_verified = (
                        payload['password'] == user.password
                    )

                    if not is_verified:
                        raise HTTPException(status_code=401, detail='Невалидный токен')
                except Exception:
                    raise HTTPException(status_code=401, detail='Невалидный токен')
        else:
            raise HTTPException(status_code=401, detail='Невалидный токен')

        return user

    async def get_auth_user_by_login(self, login):

        """ Login auth_user resolver """

        async with get_session() as s:
            sql = async_select(UserTable).filter(
                UserTable.login_phone_number == login,
                UserTable.is_active
            )
            user = (await s.execute(sql)).unique().scalars().one_or_none()

        return user

    # Авторизация администратора через полученный ранее токен
    async def token_admin(self, auth_token: str) -> AdminUserTable:

        payload = await self.decode_token(auth_token)

        if payload:

            async with get_session() as s:
                sql = async_select(AdminUserTable).filter(AdminUserTable.mobile == payload['login'],
                                                          AdminUserTable.is_active)
                user = (await s.execute(sql)).unique().scalars().one_or_none()

                if not user:
                    raise HTTPException(status_code=404, detail=f'Активный пользователь {user.mobile} не найден')
                try:
                    is_verified = (
                        payload['password'] == user.password
                    )

                    if not is_verified:
                        raise HTTPException(status_code=401, detail='Невалидный токен')
                except Exception:
                    raise HTTPException(status_code=401, detail='Невалидный токен')
        else:
            raise HTTPException(status_code=401, detail='Невалидный токен')

        return user

    async def get_admin_user_by_login(self, login):

        """ Login admin_user resolver """

        async with get_session() as s:
            sql = async_select(AdminUserTable).filter(
                AdminUserTable.mobile == login,
                AdminUserTable.is_active
            )
            user = (await s.execute(sql)).unique().scalars().one_or_none()

        return user
