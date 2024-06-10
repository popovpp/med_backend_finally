import strawberry

from strawberry.types import Info
from typing import Optional
# from kafka import KafkaProducer

from core.authorization.permissions import (IsAuthenticated, get_auth_user_by_auth_header,
                                            IsAuthenticatedOrGuest, IsAdmin, get_admin_user_by_auth_header)
from core.config.scalars import RequestResult
from core.src.common_resolvers import getting_objs
from oracle_connector.scripts.oracle_connector import call_oracle_proc
from core.sa_tables.admin import UserAdminTable
from core.sa_tables.accounts import UserRelativeTable

from .scalars import UserAdminResult, UserAdminInputAdm, UserRelativeInputAdm, UserRelativeResultAdm


@strawberry.type
class QueryAdmin:

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_test(self, info:Info) -> RequestResult:

        """Получение списка медицицинских центров тест"""

        user, _ = await get_auth_user_by_auth_header(info)

        data = [124501, None]

        result = await call_oracle_proc(data, 'solution_med.pkg_perc_acc.get_pat_info')

        return RequestResult(
            data=result,
            status_code=200,
            details='ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_user_admin_info(self,
                                  info:Info,
                                  filtering_attrs: Optional[UserAdminInputAdm] = None,
                                  ordering_attrs: Optional[UserAdminInputAdm] = None,
                                  skip: Optional[int] = 1,
                                  limit: Optional[int] = 10,
                                  desc_sorting: Optional[bool] = None) -> UserAdminResult:
        """Получение управляющей информации по таблице users"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, UserAdminTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserAdminResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAdmin])
    async def get_user_relatives_admin(
        self,
        info:Info,
        filtering_attrs: Optional[UserRelativeInputAdm] = None,
        ordering_attrs: Optional[UserRelativeInputAdm] = None,
        skip: Optional[int] = 1,
        limit: Optional[int] = 10,
        desc_sorting: Optional[bool] = None
    ) -> UserRelativeResultAdm:
        """Получение списка родственников пользователя"""

        user, _ = await get_admin_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, UserRelativeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserRelativeResultAdm(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )
