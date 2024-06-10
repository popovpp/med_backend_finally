from sqlalchemy.future import select as async_select
from sqlalchemy import select, func, and_, or_, desc

from core.config.db import get_session
from core.config.scalars import RequestResult
from core.sa_tables.accounts import UserTable
from core.authorization.auth import Auth


async def guest_registrating():

    auth = Auth()

    user = await auth.get_auth_user_by_login('guest')

    if user is not None:
        return RequestResult(status_code=422,
            details='Пользователь "guest" уже зарегистрирован в системе.'
        )

    new_patient = UserTable(
        first_name = 'guest',
        last_name = 'guest',
        phone_number = 'guest',
        email = 'guest',
        login_phone_number = 'guest'
    )
    new_patient.set_password('guest')
    new_patient.set_is_active_true()
    new_patient.set_is_verified_true()

    async with get_session() as s:
        try:
            s.add(new_patient)
            await s.commit()
        except Exception as e:
            print(e)
            result = RequestResult(
                status_code=422,
                details=f'Пользователь {new_patient.email} не зарегистрирован, повторите попытку'
            )

    async with get_session() as s:
        try:
            user = (await s.execute(async_select(UserTable).filter(
                UserTable.login_phone_number == 'guest'
            ))).unique().scalars().one_or_none()
            if user:
                result = RequestResult(
                    data = await auth.encode_token(user.login_phone_number, user.password),
                    details='Ok',
                    status_code=200
                )
            else:
                raise Exception("Пользователь в базе отсутствует")
        except Exception as e:
            print(e)
            result = RequestResult(
                status_code=422,
                details=f'Пользователь {new_patient.email} не зарегистрирован, повторите попытку'
            )
    return result
