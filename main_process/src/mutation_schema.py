import strawberry
import hashlib
from typing import Optional, List
from strawberry.types import Info

from core.config.cache_connector import CacheConnector
from core.authorization.auth import Auth
from core.authorization.permissions import (IsAuthenticated, IsAuthenticatedOrGuest,
                                            get_auth_user_by_auth_header)
from core.config.scalars import RequestResult, UserDefaultObjectIn, UserIn
from core.sa_tables.main_process import UserPurchaseTable, UserDefaultObjectTable
from core.sa_tables.accounts import UserTable
from core.src.common_resolvers import (adding_updating_obj, deleting_obj, getting_objs,
                                       getting_relatives_ids)

from .scalars import (UserPurchaseResult, UserPurchaseInput, UserPurchaseInMut,
                      UserDefaultObjectInput)
from .resolvers import (booking_access_tickets, setting_free_access_tickets,
                        changing_user_service_booking, canceling_not_paid_service,
                        mis_update_users_default_mc)


hasher= hashlib.sha256
cache = CacheConnector()
auth = Auth()


@strawberry.type
class MutationMainProcess:

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def add_user_purchase(
        self,
        info:Info,
        data_user_purchase: UserPurchaseInMut,
        data_user_purchase_id: Optional[int] = None,
        filtering_attrs: Optional[UserPurchaseInput] = None,
        ordering_attrs: Optional[UserPurchaseInput] = None,
        skip: Optional[int] = 0,
        limit: Optional[int] = 1000,
        desc_sorting: Optional[bool] = None) -> UserPurchaseResult:
        """
        Запрос на добавление редактирование покупки пользователя
        """
        # Проверка новая покупка или имеющаяся
        # Если имеющаяся, то вносить исправления можно только до момента оплаты
        if data_user_purchase_id:
            user_purchase = True#getting_obj_by_attr('data_user_purchase_id')
            if not user_purchase:#.user_payment_id:
                result = await adding_updating_obj(data_user_purchase, UserPurchaseTable, data_user_purchase_id)
            else:
                result = RequestResult(
                    status_code=422,
                    details=f"Оплаченную покупку с id={data_user_purchase_id} редактировать нельзя.% You can't edit the paid purhase with id={data_user_purchase_id}"
                )

        user, _ = await get_auth_user_by_auth_header(info)

        filtering_attrs.user_id = user.id

        result_list = await getting_objs(info, user, UserPurchaseTable,
                                         filtering_attrs,
                                         ordering_attrs,
                                         skip,
                                         limit,
                                         desc_sorting)

        return UserPurchaseResult(
            data=result_list,
            status_code=result.status_code,
            details=result.details
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def delete_user_purchase(
        self,
        info:Info,
        user_purchase_id: int
    ) -> RequestResult:
        """
        Запрос на удаление покупки пользователя
        """

        result = await deleting_obj(user_purchase_id, UserPurchaseTable)

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def set_user_default_objects(
        self,
        info: Info,
        user_default_objects:UserDefaultObjectInput
    ) -> RequestResult:
        """
        Запрос на редактирование объектов по умолчанию пользователя
        """

        user, _ = await get_auth_user_by_auth_header(info)

        if user_default_objects.default_patient_id:
        # Получаем айдишники всех родственников
            user_relatives_ids = list(await getting_relatives_ids(user.id))
            user_relatives_ids.append(user.id)

            if user_default_objects.default_patient_id not in user_relatives_ids:
                return RequestResult(
                    status_code=422,
                    details=f"You donn't have the relative id = {user_default_objects.default_patient_id}.",
                    details_ru=f"У вас нет родственника с id = {user_default_objects.default_patient_id}."
                )

        user_default_obj_list, _, _ = await getting_objs(info, user, UserDefaultObjectTable,
                                                            filtering_attrs=UserDefaultObjectInput(
                                                                user_id=user.id
                                                            ))

        if not user_default_obj_list:
            user_default_objects.user_id = user.id
            user_default_objects.default_patient_id = user.id
            user_default_obj_id = None
        else:
            user_default_obj_id = user_default_obj_list[0].id

        result = await adding_updating_obj(user_default_objects, UserDefaultObjectTable, user_default_obj_id)

        if result.status_code != 200:
            return result

        if user_default_objects.default_medical_center_id:
            result = await mis_update_users_default_mc(
                user,
                user_default_objects.default_medical_center_id
            )

        return result

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def book_access_tickets(
        self,
        info: Info,
        main_access_ticket_client_id: str,
        access_tickets_client_ides: Optional[List[str]] = None
    ) -> RequestResult:
        """
        Запрос на бронирование номерков
        """

        if main_access_ticket_client_id not in access_tickets_client_ides:
            return RequestResult(
                status_code=422,
                details='main_access_ticket_client_id must be included in the access_tickets_client_ides',
                details_ru='Главный тикет должен быть в составе передавемого списка'
            )

        user, _ = await get_auth_user_by_auth_header(info)

        filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )

        if user.login_phone_number != 'guest':
            user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, filtering_attrs)
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        result = await booking_access_tickets(
            patient, main_access_ticket_client_id,
            access_tickets_client_ides
        )

        return result

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def set_free_access_tickets(
        self,
        info: Info,
        main_access_ticket_client_id: str,
        ex_guest: Optional[bool] = None
    ) -> RequestResult:
        """
        Освобождение забронированых ранее номерков
        """

        user, _ = await get_auth_user_by_auth_header(info)

        filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )

        if user.login_phone_number != 'guest':
            user_default_objs, _, _ = await getting_objs(
                info, user, UserDefaultObjectTable, filtering_attrs
            )
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        if ex_guest:
            filtering_attrs = UserIn(
                login_phone_number='guest'
            )
            user_guest, _, _ = await getting_objs(info, user, UserTable, filtering_attrs)
            patient = user_guest[0]

        result = await setting_free_access_tickets(patient.client_id, main_access_ticket_client_id)

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def change_user_service_booking(
        self,
        info: Info,
        user_service_cart_client_id: str,
        new_main_access_ticket_client_id: str,
        new_tickets_client_ids: List[str]
    ) -> RequestResult:
        """
        Перезапись услуги на другой номерок
        """

        user, _ = await get_auth_user_by_auth_header(info)

        if new_main_access_ticket_client_id not in new_tickets_client_ids:
            return RequestResult(
                status_code=422,
                details='main_access_ticket_client_id must be included in the access_tickets_client_ides',
                details_ru='Главный тикет должен быть в составе передавемого списка'
            )

        result = await changing_user_service_booking(
            user_service_cart_client_id,
            new_main_access_ticket_client_id,
            new_tickets_client_ids
        )

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def cancel_not_paid_service(
        self,
        info: Info,
        user_service_cart_client_id: str
    ) -> RequestResult:
        """
        Отмена неоплаченной услуги
        """

        user, _ = await get_auth_user_by_auth_header(info)

        result = await canceling_not_paid_service(
            user,
            user_service_cart_client_id
        )

        return result
