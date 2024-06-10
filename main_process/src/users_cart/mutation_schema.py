import strawberry
import hashlib
import json
from typing import Optional
from strawberry.types import Info
# from kafka import KafkaProducer

from core.config.cache_connector import CacheConnector
from core.authorization.auth import Auth
from core.authorization.permissions import (IsAuthenticated, IsAuthenticatedOrGuest, get_auth_user_by_auth_header,
                                            get_auth_token_by_auth_header)
from core.config.scalars import RequestResult
from core.sa_tables.main_process import UserPurchaseTable, UserDefaultObjectTable, UserServiceCartTable
from core.src.common_resolvers import adding_updating_obj, deleting_obj, getting_objs
# from faustians.config.settings import MOVE_CACHE_CART_TO_DATABASE
# from core.src.utils import input_obj_constructor_with_fk

from .scalars import (UserServiceCartInput, UserServiceCartOutputCache, UserServiceCartInputMut, UserServiceCartOutput,
                      UserServiceCartOutputResult, UserServiceCartOutputCacheResult)
from .resolvers import (filling_data_user_service, add_update_item_to_cache_cart, delete_item_from_cache_cart,
                        move_cart_from_cache_to_database)


hasher= hashlib.sha256
cache = CacheConnector()
auth = Auth()


@strawberry.type
class MutationMainProcessCart:

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def add_update_service_to_user_cart(
        self,
        info:Info,
        data_user_service: UserServiceCartInputMut,
        user_service_cart_id: Optional[int] = None,
        filtering_attrs: Optional[UserServiceCartInput] = None,
        ordering_attrs: Optional[UserServiceCartInput] = None,
        skip: Optional[int] = 0,
        limit: Optional[int] = 1000,
        desc_sorting: Optional[bool] = None) -> UserServiceCartOutputResult | UserServiceCartOutputCacheResult:
        """
        Запрос на добавление услуги в корзину пользователя
        """

        user, token = await get_auth_token_by_auth_header(info)

        if user.login_phone_number == 'guest':
            key = token[-11:]
            result = await add_update_item_to_cache_cart(info, user, key, data_user_service, user_service_cart_id)
        else:
            # if user_service_cart_id is not None:
            #     data_user_service.id = user_service_cart_id

            data_user_service.user_id = user.id

            data_user_service_full = await filling_data_user_service(user.id, data_user_service.__dict__)

            result = await adding_updating_obj(data_user_service_full, UserServiceCartTable, user_service_cart_id)

            if result.status_code != 200:
                return result
            else:
                if filtering_attrs:
                    filtering_attrs.user_id = user.id
                else:
                    filtering_attrs = UserServiceCartInput(
                        user_id=user.id,
                    )
                if ordering_attrs:
                    ordering_attrs.id = 0
                else:
                    ordering_attrs = UserServiceCartInput(
                        id=0
                    )
                result_list, _, _ = await getting_objs(info, user, UserServiceCartTable,
                                                       filtering_attrs,
                                                       ordering_attrs,
                                                       skip,
                                                       limit,
                                                       desc_sorting)
                result = UserServiceCartOutputResult(
                    data=result_list,
                    status_code=200,
                    details_ru='Ок',
                    details='Ok'
                )

        return result

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def delete_sevice_from_user_cart(
        self,
        info:Info,
        user_service_cart_id: Optional[int] = None,
        filtering_attrs: Optional[UserServiceCartInput] = None,
        ordering_attrs: Optional[UserServiceCartInput] = None,
        skip: Optional[int] = 0,
        limit: Optional[int] = 1000,
        desc_sorting: Optional[bool] = None) -> UserServiceCartOutputResult | UserServiceCartOutputCacheResult:
        """
        Запрос на удаление услуги из корзины пользователя
        """

        user, token = await get_auth_token_by_auth_header(info)

        if user.login_phone_number == 'guest':

            key = token[-11:]

            await delete_item_from_cache_cart(key, user_service_cart_id)

            user_services_cart = sorted(json.loads(cache.get(key))["data"], key=lambda x: x['id'])

            result = UserServiceCartOutputCacheResult(
                data=[UserServiceCartOutputCache(**x) for x in user_services_cart],
                status_code=200,
                details='Ok'
            )
        else:
            result = await deleting_obj(user_service_cart_id, UserServiceCartTable)

            if result.status_code != 200:
                return result
            else:
                if filtering_attrs:
                    filtering_attrs.user_id = user.id
                else:
                    filtering_attrs = UserServiceCartInput(
                        user_id=user.id,
                    )
                if ordering_attrs:
                    ordering_attrs.id = 0
                else:
                    ordering_attrs = UserServiceCartInput(
                        id=0
                    )
                result_list, _, _ = await getting_objs(info, user, UserServiceCartTable,
                                                       filtering_attrs,
                                                       ordering_attrs,
                                                       skip,
                                                       limit,
                                                       desc_sorting)
                result = UserServiceCartOutputResult(
                    data=result_list,
                    status_code=200,
                    details_ru='Ок',
                    details='Ok'
                )

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def fix_cart_for_registrated_user(
        self,
        info:Info,
        half_guest_token: str,
        ) -> RequestResult:
        """
        Запрос на перенос корзины вновь зарегистрированного пользователя из кэша в базу.
        """

        user, _ = await get_auth_token_by_auth_header(info)

        key = half_guest_token[-11:]

        result = await move_cart_from_cache_to_database(user.id, key)

        return result
