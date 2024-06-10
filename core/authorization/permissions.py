import typing
from strawberry.permission import BasePermission
from strawberry.types import Info
from fastapi import Request, WebSocket

from .auth import Auth
# from core.config.db import get_session


async def get_auth_token_by_auth_header(info: Info):

    auth_handler = Auth()

    request: typing.Union[Request, WebSocket] = info.context["request"]

    try:
        auth_header_list = request.headers['Authorization'].split()
        bearer = auth_header_list[0]
        token = auth_header_list[1]
        sub = await auth_handler.decode_token(auth_header_list[1])
    except Exception:
        return None, None

    if bearer != 'Bearer':
        return None, None

    if sub is not None:
        login = sub['login']
        # password = sub['password']
    else:
        return None, None

    user = await auth_handler.get_auth_user_by_login(login)

    return user, token


async def get_auth_user_by_auth_header(info: Info):

    auth_handler = Auth()

    request: typing.Union[Request, WebSocket] = info.context["request"]

    try:
        auth_header_list = request.headers['Authorization'].split()
        bearer = auth_header_list[0]
        sub = await auth_handler.decode_token(auth_header_list[1])
    except Exception:
        return None, None

    if bearer != 'Bearer':
        return None, None

    if sub is not None:
        login = sub['login']
        password = sub['password']
    else:
        return None, None

    user = await auth_handler.get_auth_user_by_login(login)

    return user, password


async def get_admin_user_by_auth_header(info: Info):

    auth_handler = Auth()

    request: typing.Union[Request, WebSocket] = info.context["request"]

    try:
        auth_header_list = request.headers['Authorization'].split()
        bearer = auth_header_list[0]
        sub = await auth_handler.decode_token(auth_header_list[1])
    except Exception:
        return None, None

    if bearer != 'Bearer':
        return None, None

    if sub is not None:
        login = sub['login']
        password = sub['password']
    else:
        return None, None

    user = await auth_handler.get_admin_user_by_login(login)

    return user, password


class IsAuthenticated(BasePermission):

    message = "User is not authenticated"

    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:

        user, password = await get_auth_user_by_auth_header(info)

        if not user:
            return False

        is_verified = password == user.password

        if not is_verified:
            return False

        return True


class IsAuthenticatedOrGuest(BasePermission):

    message = "User is not authenticated"

    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:

        user, password = await get_auth_user_by_auth_header(info)

        if not user:
                return False

        # Если юзер Гость
        if user.login_phone_number == 'guest' and password == 'guest':
            return True
        else:
            # Если юзер авторизован
            is_verified = password == user.password
            if not is_verified:
                return False
            else:
                return True


class IsAdmin(BasePermission):

    message = "Admin is not authenticated"

    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:

        user, password = await get_admin_user_by_auth_header(info)

        if not user:
            return False

        is_verified = password == user.password

        if not is_verified:
            return False

        return True
