import asyncio
from typing import Any
import getpass

from sqlalchemy.future import select as async_select

from core.config.db import get_session
from core.sa_tables.accounts import AdminUserTable


async def create_superuser() -> Any:

    async with get_session() as s:

        superuser_sql = async_select(
            AdminUserTable
        ).filter(
            AdminUserTable.is_superuser == True
        )

        superuser = (await s.execute(superuser_sql)).scalars().one_or_none()

        if not superuser:
            user_in = {}
            user_in['email'] = input('Введите email:')
            user_in['mobile'] = input('Введите номер телефона:')
            user_in['password'] = getpass.getpass('Введите пароль:')

            user_sql = async_select(
                AdminUserTable
            ).filter(
                AdminUserTable.mobile == user_in['mobile']
            )

            user = (await s.execute(user_sql)).scalars().one_or_none()

            if user:
                print("User with same mobile already exists")
            else:
                user = AdminUserTable()
                user.email = user_in['email']
                user.mobile = user_in['mobile']
                user.set_password(user_in['password'])
                user.set_is_active_true()
                user.set_is_superuser_true()
                # user.set_is_verified_true()

                s.add(user)
                await s.commit()

                if user.id:
                    print('Superuser has been created')
                    print({'id': user.id, 'email': user.email})
                else:
                    print('Superuser was not created')
        else:
            print("Superuser already exists")


def main():
    asyncio.run(create_superuser())


if __name__=="__main__":
    main()
