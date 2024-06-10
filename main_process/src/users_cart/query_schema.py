# import time
import json
import strawberry
from strawberry.types import Info
from typing import Optional, List
# from datetime import timedelta
# from kafka import KafkaProducer

from core.config.cache_connector import CacheConnector
from core.authorization.permissions import (IsAuthenticated, get_auth_user_by_auth_header, IsAuthenticatedOrGuest,
                                            get_auth_token_by_auth_header)
from core.sa_tables.main_process import (UserServiceCartTable)
# from core.sa_tables.accounts import MedicalCenterTable, CityTable
from core.src.common_resolvers import getting_objs
# from .resolvers import (getting_service_group1, getting_service_group2, getting_services_with_price,
#                         getting_service_group3)
from .scalars import (UserServiceCartOutputResult, UserServiceCartInput, UserServiceCartOutput,
                      UserServiceCartOutputCacheResult, UserServiceCartOutputCache)


cache = CacheConnector()


@strawberry.type
class QueryMainProcessCart:

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_user_service_cart(self,
                                    info:Info,
                                    filtering_attrs: Optional[UserServiceCartInput] = None,
                                    ordering_attrs: Optional[UserServiceCartInput] = None,
                                    skip: Optional[int] = 1,
                                    limit: Optional[int] = 1000,
                                    desc_sorting: Optional[bool] = None) -> UserServiceCartOutputResult | UserServiceCartOutputCacheResult:

        """Получение корзин пользователей"""

        user, token = await get_auth_token_by_auth_header(info)

        if user.login_phone_number == 'guest':

            key = token[-11:]

            try:
                user_services_cart = sorted(json.loads(cache.get(key))["data"], key=lambda x: x['id'])
            except Exception as e:
                user_services_cart = []

            result = UserServiceCartOutputCacheResult(
                data=[UserServiceCartOutputCache(**x) for x in user_services_cart],
                status_code=200,
                details='Ok',
                details_ru='Ок'
            )
        else:
            if filtering_attrs is not None and filtering_attrs.user_id == None:
                filtering_attrs.user_id = user.id
            elif filtering_attrs is not None and filtering_attrs.user_id != None:
                pass
            else:
                filtering_attrs = UserServiceCartInput(
                    user_id=user.id
                )

            ordering_attrs = UserServiceCartOutput(
                id=1
            )

            result_list, records_count, pages_count = await getting_objs(info, user, UserServiceCartTable,
                                                                         filtering_attrs,
                                                                         ordering_attrs,
                                                                         skip,
                                                                         limit,
                                                                         desc_sorting)
            result = UserServiceCartOutputResult(
                data=result_list,
                status_code=200,
                details='Ok',
                details_ru='Ок',
                records_count=records_count,
                pages_count=pages_count
            )

        return result
