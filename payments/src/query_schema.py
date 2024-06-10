import strawberry
from datetime import datetime, timedelta
from typing import Optional, List
from strawberry.types import Info

from core.authorization.permissions import IsAuthenticated, get_auth_user_by_auth_header
from core.config.scalars import (RequestResult, UserDefaultObjectIn, PaymentTypeIn,
                                 UserServiceCartIn, UserPurchaseIn)
from core.sa_tables.main_process import UserDefaultObjectTable, UserServiceCartTable
from core.sa_tables.accounts import MedicalCenterTable
from core.sa_tables.main_process import UserPaymentTable
from core.src.common_resolvers import getting_objs, getting_relatives_ids
from payments.config.settings import POSTPONED_PAYMENT
from .resolvers import (getting_unused_advances_sum,
                        getting_services_with_current_debt, getting_current_debt,
                        getting_payments_history, getting_returned_payment_mrssage)
from .scalars import (MedicalCenterInputPay, McentersUnuseAdvancesSumResult,
                      UserPaymentInputPay, UserPaymentResultPay, ServiceCurrentDebtResult,
                      CurrentDebtResult, HistoryPaymentsResult, UserPaymentWithServices)
# from .scripts_initpro import initpro_document_registration, get_document_registration_result
# from .utils import create_initpro_payload, creating_receipt


@strawberry.type
class QueryPayments:

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_unused_advances_sum(self, info:Info,
                                      medical_center_id: Optional[int] = None) -> McentersUnuseAdvancesSumResult:

        """Получение суммы неиспользованных авансов"""

        # Получаем пациента по умолчанию
        user, _ = await get_auth_user_by_auth_header(info)
        filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, filtering_attrs)
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        # Получаем медицинский центр
        if medical_center_id:
            filtering_attrs = MedicalCenterInputPay(
                id=medical_center_id
            )
            medical_center_objs, _, _ = await getting_objs(info, user, MedicalCenterTable, filtering_attrs)
            if not medical_center_objs:
                return RequestResult(
                    status_code=422,
                    details_ru=f'Медицинского центра с идентификатором {medical_center_id} не существует',
                    details=f"The medical center with nubber {medical_center_id} doesn't exist"
                )
            lpu_id = medical_center_objs[0].lpu_id
        else:
            lpu_id = None

        result_list = await getting_unused_advances_sum(patient, lpu_id)

        return McentersUnuseAdvancesSumResult(
            data=result_list,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_postponed_payments(self,
                                          info:Info,
                                          filtering_attrs: Optional[UserPaymentInputPay] = None,
                                          ordering_attrs: Optional[UserPaymentInputPay] = None,
                                          medical_center_id: Optional[int] = None,
                                          service_id: Optional[int] = None,
                                          skip: Optional[int] = 1,
                                          limit: Optional[int] = 10000,
                                          desc_sorting: Optional[bool] = None) -> UserPaymentResultPay:

        """Получение отложенных платежей пользователя"""

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        user_filtering_attrs = UserDefaultObjectIn(
            user_id=[user.id]
        )
        user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, user_filtering_attrs)
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        # Получаем айдишники всех родственников
        relatives_ids = await getting_relatives_ids(user.id)
        relatives_ids.append(user.id)

        if filtering_attrs is not None:
            filtering_attrs.payment_type = PaymentTypeIn(
                client_id = int(POSTPONED_PAYMENT)
            )
            if filtering_attrs.user_id is None:
                filtering_attrs.user_id = [patient.id]
            else:
                for item in filtering_attrs.user_id:
                    if item not in relatives_ids:
                        return UserPaymentResultPay(
                            status_code=422,
                            details=f'The patient {item} is not your relative',
                            details_ru=f'Пациент {item} не является вашим родственником'
                        )
        else:
            filtering_attrs = UserPaymentInputPay(
                payment_type = PaymentTypeIn(
                    client_id = int(POSTPONED_PAYMENT)
                ),
                user_id=[patient.id]
            )

        result_list, records_count, pages_count = await getting_objs(info, user, UserPaymentTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        user_payments_ids = [x.id for x in result_list]

        services_cart_filtering_attrs = UserServiceCartIn(
            user_purchase = UserPurchaseIn(
                user_payment_id = user_payments_ids
            ),
            medical_center_id = medical_center_id,
            service_id = service_id
        )

        services_result_list, records_count, pages_count = await getting_objs(info, user, UserServiceCartTable,
                                                                              services_cart_filtering_attrs,
                                                                              limit=limit)

        payment_services_dict = {}
        finally_result_list = []

        for item in services_result_list:
            # if item.user_purchase.user_payment.lpu_id != None:
            try:
                payment_services_dict[item.user_purchase.user_payment_id][0].append(item.service.name_for_lk)
            except Exception:
                payment_services_dict[item.user_purchase.user_payment_id] = ([item.service.name_for_lk], item.medical_center)

        for item in services_result_list:
            try:
                finally_result_list.append(
                    UserPaymentWithServices(
                        payment=item.user_purchase.user_payment,
                        services_names=payment_services_dict[item.user_purchase.user_payment_id][0],
                        medical_center=payment_services_dict[item.user_purchase.user_payment_id][1]
                    )
                )
            except Exception as e:
                print(e)

        return UserPaymentResultPay(
            data=finally_result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_services_with_current_debt(self, info:Info,
                                             medical_center_ids: Optional[List[int]] = None,
                                             patient_ids: Optional[List[int]] = None,
                                             payment_ids: Optional[List[int]] = None) -> ServiceCurrentDebtResult:

        """Получение списка услуг, по которым есть задолженность по оплате"""

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем айдишники всех родственников
        relatives_ids = await getting_relatives_ids(user.id)
        relatives_ids.append(user.id)
        if not patient_ids:
            patient_ids = relatives_ids
        else:
            for person in patient_ids:
                if person not in relatives_ids:
                    return HistoryPaymentsResult(
                        status_code=422,
                        details=f'The patient with number {person} is not your relatives',
                        details_ru=f'Пациент с номером {person} не является вашим родственником'
                    )

        result_list = await getting_services_with_current_debt(
            info, user,
            medical_center_ids=medical_center_ids,
            patient_ids=patient_ids,
            payment_ids=payment_ids
        )

        return ServiceCurrentDebtResult(
            data=result_list,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_current_debt(self, info:Info,
                               medical_center_ids: Optional[List[int]] = None,
                               patient_ids: Optional[List[int]] = None) -> CurrentDebtResult:

        """Получение текущей задолженности пользователя по оплате"""

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем айдишники всех родственников
        relatives_ids = await getting_relatives_ids(user.id)
        relatives_ids.append(user.id)
        if not patient_ids:
            patient_ids = relatives_ids
        else:
            for person in patient_ids:
                if person not in relatives_ids:
                    return HistoryPaymentsResult(
                        status_code=422,
                        details=f'The patient with number {person} is not your relatives',
                        details_ru=f'Пациент с номером {person} не является вашим родственником'
                    )

        result_list = await getting_current_debt(
            info, user,
            medical_center_ids=medical_center_ids,
            patient_ids=patient_ids
        )

        return CurrentDebtResult(
            data=result_list,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_payments_history(self, info:Info,
                                   start_date: str,
                                   end_date: str,
                                   patient_ids: Optional[List[int]] = None) -> HistoryPaymentsResult:
        """Получение истории платежей пользователя"""

        user, _ = await get_auth_user_by_auth_header(info)

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(hours=23, minutes=59)
            except Exception as e:
                print(e)
                return HistoryPaymentsResult(
                    details="The fields 'start_date' or 'end_date' or both are wrong. The right format is 'YYYY-MM-DD'.",
                    details_ru="Поля start_date или end_date или оба имеют ошибочный формат. Правильный формат 'YYYY-MM-DD'.",
                    status_code=422
                )
        else:
            return HistoryPaymentsResult(
                    details="The fields 'start_date' and 'end_date' are required",
                    details_ru="Поля start_date и end_date являются обязательными",
                    status_code=422
                )

        # Получаем айдишники всех родственников
        relatives_ids = await getting_relatives_ids(user.id)
        relatives_ids.append(user.id)
        if not patient_ids:
            patient_ids = relatives_ids
        else:
            for person in patient_ids:
                if person not in relatives_ids:
                    return HistoryPaymentsResult(
                        status_code=422,
                        details=f'The patient with number {person} is not your relatives',
                        details_ru=f'Пациент с номером {person} не является вашим родственником'
                    )

        result_list = await getting_payments_history(
            info, user,
            start_date,
            end_date,
            patient_ids=patient_ids
        )

        return HistoryPaymentsResult(
            data=result_list,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_returned_payment_message(
        self, info:Info,
        user_service_cart_client_id: str
    ) -> RequestResult:

        """Получение сообщения о возврате платежа"""

        user, _ = await get_auth_user_by_auth_header(info)

        result = await getting_returned_payment_mrssage(user, user_service_cart_client_id)

        return result
