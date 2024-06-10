import time
import strawberry
from strawberry.types import Info
from typing import Optional, List
from datetime import timedelta, datetime, date

from core.config.cache_connector import CacheConnector
from core.authorization.permissions import (IsAuthenticated, get_auth_user_by_auth_header, IsAuthenticatedOrGuest)
from core.sa_tables.main_process import (ServiceTypeTable, MedicalPositionTable,
                                         ServiceTable, MedicalSpecialityTable, DoctorTable, DoctorMspecialityTable,
                                         StaffTypeTable, DoctorCategoryTable, DoctorStatusTypeTable, DoctorStatusTable,
                                         PatientTypeTable, DoctorMedicalCenterTable, DoctorPatientTypeTable,
                                         ServiceMedicalSpecialityTable, ComplexServiceTable, ComplexServiceItemTable,
                                         FinancialTypeTable, ShifrTable, PolicyTable, UserSubscribeTable,
                                         DoctorReplacementTable, SubscribeDoctorTable, PackTypeTable,
                                         SubscribeServicePackTable, SubscribeSpackRecordTable, ShifrDiscountPeriodTable,
                                         ShifrDiscountTable, UserPurchaseTable, PricePeriodTable, PriceNameTable,
                                         PriceTable, PaymentTypeTable, UserPaymentTable, UserPurchaseReturnTable,
                                         RefuseReasonTable, UserServicePlanTable,
                                         AccessTicketTable, DoctorMedicalCenterServiceTable, MedicalCenterPriceNameTable,
                                         UserDefaultObjectTable)
from core.sa_tables.accounts import MedicalCenterTable, CityTable
from core.src.common_resolvers import getting_objs, getting_relatives_ids
from core.src.utils import get_search_words
from core.config.scalars import (UserDefaultObjectIn, PolicyIn, SubscribeServicePackIn,
                                 UserSubscribeIn, DoctorMedicalCenterIn, MedicalCenterIn)
from .resolvers import (getting_service_group1, getting_service_group2, getting_services_with_price,
                        getting_service_group3, finding_access_tickets_ides, getting_subscribe_info_blocks,
                        getting_events_calendar, getting_visits_history, getting_objs_rew)
from .scalars import (MedicalCenterResult, CityResult, MedicalPositionResult, ServiceTypeResult,
                      ServiceResult, MedicalCenterInput, ServiceTypeInput, CityInput, MedicalPositionInput,
                      ServiceInput, MedicalSpecialityInput, MedicalSpecialityResult, DoctorResult, DoctorInput,
                      DoctorMspecialityResult, DoctorMspecialityInput, StaffTypeInput, StaffTypeResult,
                      DoctorCategoryResult, DoctorCategoryInput,
                      DoctorStatusTypeResult, DoctorStatusTypeInput, DoctorStatusResult,
                      DoctorStatusInput, PatientTypeResult, PatientTypeInput, DoctorMedicalCenterResult,
                      DoctorMedicalCenterInput, DoctorPatientTypeResult, DoctorPatientTypeInput,
                      ServiceMedicalSpecialityResult, ServiceMedicalSpecialityInput, ComplexServiceResult,
                      ComplexServiceInput, ComplexServiceItemResult, ComplexServiceItemInput, FinancialTypeInput,
                      FinancialTypeResult, ShifrResult, ShifrInput, PolicyResult, PolicyInput, UserSubscribeResult,
                      UserSubscribeInput, DoctorReplacementResult, DoctorReplacementInput, SubscribeDoctorResult,
                      SubscribeDoctorInput, PackTypeResult, PackTypeInput, SubscribeServicePackResult,
                      SubscribeServicePackInput, SubscribeSpackRecordResult, SubscribeSpackRecordInput,
                      ShifrDiscountPeriodInput, ShifrDiscountPeriodResult, ShifrDiscountResult, ShifrDiscountInput,
                      ServiceGroupResult, UserPurchaseResult, UserPurchaseInput, PricePeriodResult, PricePeriodInput,
                      PriceNameResult, PriceNameInput, PriceResult, PriceInput, PaymentTypeResult, PaymentTypeInput,
                      UserPaymentResult, UserPaymentInput, UserPurchaseReturnResult, UserPurchaseReturnInput,
                      RefuseReasonResult, RefuseReasonInput,
                      UserServicePlanResult, UserServicePlanInput, AccessTicketResult, AccessTicketInput,
                      DoctorMedicalCenterServiceResult, DoctorMedicalCenterServiceInput,
                      MedicalCenterPriceNameResult, MedicalCenterPriceNameInput, UserDefaultObjectResult,
                      UserDefaultObjectInput, SubscribeInfoBlocksResult, EventsCalendarResult,
                      AccessTicketInputSort, VisitHistoryRecordResult)


cache = CacheConnector()


@strawberry.type
class QueryMainProcess:

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_medical_centers(self, info:Info,
                                  filtering_attrs: Optional[MedicalCenterInput] = None,
                                  ordering_attrs: Optional[MedicalCenterInput] = None,
                                  skip: Optional[int] = 1,
                                  limit: Optional[int] = 1000,
                                  desc_sorting: Optional[bool] = None) -> MedicalCenterResult:

        """Получение списка медицицинских центров"""

        user, _ = await get_auth_user_by_auth_header(info)

        if filtering_attrs:
            filtering_attrs.show_in_lk = True
        else:
            filtering_attrs = MedicalCenterInput(
                show_in_lk=True
            )

        result_list, records_count, pages_count = await getting_objs(info, user, MedicalCenterTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return MedicalCenterResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_services_types(self, info:Info,
                                 filtering_attrs: Optional[ServiceTypeInput] = None,
                                 ordering_attrs: Optional[ServiceTypeInput] = None,
                                 skip: Optional[int] = 1,
                                 limit: Optional[int] = 1000,
                                 desc_sorting: Optional[bool] = None
                                 ) -> ServiceTypeResult:

        """Получение спсика типов медицинских услуг"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, ServiceTypeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return ServiceTypeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_cities(self, info:Info,
                         filtering_attrs: Optional[CityInput] = None,
                         ordering_attrs: Optional[CityInput] = None,
                         skip: Optional[int] = 1,
                         limit: Optional[int] = 1000,
                         desc_sorting: Optional[bool] = None) -> CityResult:

        """Получение списка городов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, CityTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return CityResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_medical_positions(self, info:Info,
                                    filtering_attrs: Optional[MedicalPositionInput] = None,
                                    ordering_attrs: Optional[MedicalPositionInput] = None,
                                    skip: Optional[int] = 1,
                                    limit: Optional[int] = 1000,
                                    desc_sorting: Optional[bool] = None) -> MedicalPositionResult:

        """Получение списка направлений медицинских услуг"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, MedicalPositionTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return MedicalPositionResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_services(self,
                           info:Info,
                           filtering_attrs: Optional[ServiceInput] = None,
                           ordering_attrs: Optional[ServiceInput] = None,
                           skip: Optional[int] = 1,
                           limit: Optional[int] = 1000,
                           desc_sorting: Optional[bool] = None) -> ServiceResult:

        """Получение спсика медицинских услуг"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, ServiceTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return ServiceResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_medical_specialities(self,
                           info:Info,
                           filtering_attrs: Optional[MedicalSpecialityInput] = None,
                           ordering_attrs: Optional[MedicalSpecialityInput] = None,
                           skip: Optional[int] = 1,
                           limit: Optional[int] = 1000,
                           desc_sorting: Optional[bool] = None) -> MedicalSpecialityResult:

        """Получение спсика медицинских специальностей"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, MedicalSpecialityTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return MedicalSpecialityResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_doctors(self,
                           info:Info,
                           filtering_attrs: Optional[DoctorInput] = None,
                           ordering_attrs: Optional[DoctorInput] = None,
                           skip: Optional[int] = 1,
                           limit: Optional[int] = 1000,
                           desc_sorting: Optional[bool] = None) -> DoctorResult:

        """Получение списка докторов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_doctors_mspecialities(self,
                           info:Info,
                           filtering_attrs: Optional[DoctorMspecialityInput] = None,
                           ordering_attrs: Optional[DoctorMspecialityInput] = None,
                           skip: Optional[int] = 1,
                           limit: Optional[int] = 1000,
                           desc_sorting: Optional[bool] = None) -> DoctorMspecialityResult:

        """Получение спсика медицинских специальностей"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorMspecialityTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorMspecialityResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_staff_types(self,
                              info:Info,
                              filtering_attrs: Optional[StaffTypeInput] = None,
                              ordering_attrs: Optional[StaffTypeInput] = None,
                              skip: Optional[int] = 1,
                              limit: Optional[int] = 1000,
                              desc_sorting: Optional[bool] = None) -> StaffTypeResult:

        """Получение спсика типов персонала"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list = []

        result_list, records_count, pages_count = await getting_objs(info, user, StaffTypeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return StaffTypeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_doctor_categories(self,
                                    info:Info,
                                    filtering_attrs: Optional[DoctorCategoryInput] = None,
                                    ordering_attrs: Optional[DoctorCategoryInput] = None,
                                    skip: Optional[int] = 1,
                                    limit: Optional[int] = 1000,
                                    desc_sorting: Optional[bool] = None) -> DoctorCategoryResult:

        """Получение спсика категорий доктора"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorCategoryTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorCategoryResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_doctor_status_types(self,
                                      info:Info,
                                      filtering_attrs: Optional[DoctorStatusTypeInput] = None,
                                      ordering_attrs: Optional[DoctorStatusTypeInput] = None,
                                      skip: Optional[int] = 1,
                                      limit: Optional[int] = 1000,
                                      desc_sorting: Optional[bool] = None) -> DoctorStatusTypeResult:

        """Получение спсика типов статусов доктора"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorStatusTypeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorStatusTypeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_doctor_status(self,
                                info:Info,
                                filtering_attrs: Optional[DoctorStatusInput] = None,
                                ordering_attrs: Optional[DoctorStatusInput] = None,
                                skip: Optional[int] = 1,
                                limit: Optional[int] = 1000,
                                desc_sorting: Optional[bool] = None) -> DoctorStatusResult:

        """Получение списка статусов доктора"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorStatusTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorStatusResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_patient_type(self,
                               info:Info,
                               filtering_attrs: Optional[PatientTypeInput] = None,
                               ordering_attrs: Optional[PatientTypeInput] = None,
                               skip: Optional[int] = 1,
                               limit: Optional[int] = 1000,
                               desc_sorting: Optional[bool] = None) -> PatientTypeResult:

        """Получение списка типов пациентов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, PatientTypeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return PatientTypeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_doctor_medical_center(self,
                                        info:Info,
                                        filtering_attrs: Optional[DoctorMedicalCenterInput] = None,
                                        ordering_attrs: Optional[DoctorMedicalCenterInput] = None,
                                        skip: Optional[int] = 1,
                                        limit: Optional[int] = 1000,
                                        desc_sorting: Optional[bool] = None) -> DoctorMedicalCenterResult:

        """Получение списка типов пациентов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorMedicalCenterTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorMedicalCenterResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_doctor_patient_type(self,
                                      info:Info,
                                      filtering_attrs: Optional[DoctorPatientTypeInput] = None,
                                      ordering_attrs: Optional[DoctorPatientTypeInput] = None,
                                      skip: Optional[int] = 1,
                                      limit: Optional[int] = 1000,
                                      desc_sorting: Optional[bool] = None) -> DoctorPatientTypeResult:

        """Получение списка типов пациентов доктора"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorPatientTypeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorPatientTypeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_service_medical_speciality(self,
                                             info:Info,
                                             filtering_attrs: Optional[ServiceMedicalSpecialityInput] = None,
                                             ordering_attrs: Optional[ServiceMedicalSpecialityInput] = None,
                                             skip: Optional[int] = 1,
                                             limit: Optional[int] = 1000,
                                             desc_sorting: Optional[bool] = None) -> ServiceMedicalSpecialityResult:

        """Получение списка услуг медицинских специальностей"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, ServiceMedicalSpecialityTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return ServiceMedicalSpecialityResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_complex_service(self,
                                  info:Info,
                                  filtering_attrs: Optional[ComplexServiceInput] = None,
                                  ordering_attrs: Optional[ComplexServiceInput] = None,
                                  skip: Optional[int] = 1,
                                  limit: Optional[int] = 1000,
                                  desc_sorting: Optional[bool] = None) -> ComplexServiceResult:

        """Получение списка комплексных услуг"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, ComplexServiceTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return ComplexServiceResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_complex_service_item(self,
                                       info:Info,
                                       filtering_attrs: Optional[ComplexServiceItemInput] = None,
                                       ordering_attrs: Optional[ComplexServiceItemInput] = None,
                                       skip: Optional[int] = 1,
                                       limit: Optional[int] = 1000,
                                       desc_sorting: Optional[bool] = None) -> ComplexServiceItemResult:

        """Получение списка элементов комплексных услуг"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, ComplexServiceItemTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return ComplexServiceItemResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_financial_type(self,
                                       info:Info,
                                       filtering_attrs: Optional[FinancialTypeInput] = None,
                                       ordering_attrs: Optional[FinancialTypeInput] = None,
                                       skip: Optional[int] = 1,
                                       limit: Optional[int] = 1000,
                                       desc_sorting: Optional[bool] = None) -> FinancialTypeResult:

        """Получение списка элементов комплексных услуг"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, FinancialTypeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return FinancialTypeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_shifr(self,
                        info:Info,
                        filtering_attrs: Optional[ShifrInput] = None,
                        ordering_attrs: Optional[ShifrInput] = None,
                        skip: Optional[int] = 1,
                        limit: Optional[int] = 1000,
                        desc_sorting: Optional[bool] = None) -> ShifrResult:

        """Получение списка элементов комплексных услуг"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, ShifrTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return ShifrResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_policy(self,
                         info:Info,
                         filtering_attrs: Optional[PolicyInput] = None,
                         ordering_attrs: Optional[PolicyInput] = None,
                         skip: Optional[int] = 1,
                         limit: Optional[int] = 1000,
                         desc_sorting: Optional[bool] = None) -> PolicyResult:

        """Получение списка полисов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, PolicyTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return PolicyResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_subscribe(self,
                                 info:Info,
                                 filtering_attrs: Optional[UserSubscribeInput] = None,
                                 ordering_attrs: Optional[UserSubscribeInput] = None,
                                 skip: Optional[int] = 1,
                                 limit: Optional[int] = 1000,
                                 desc_sorting: Optional[bool] = None) -> UserSubscribeResult:

        """Получение списка абонементов"""

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        default_obj_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, default_obj_filtering_attrs)

        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        # Фильтруем по пациенту
        if filtering_attrs:
            filtering_attrs.policy.user_id = patient.id
        else:
            filtering_attrs = UserSubscribeInput(
                policy=PolicyIn(
                    user_id=patient.id
                )
            )

        result_list, records_count, pages_count = await getting_objs(info, patient, UserSubscribeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserSubscribeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_doctor_replacement(self,
                                     info:Info,
                                     filtering_attrs: Optional[DoctorReplacementInput] = None,
                                     ordering_attrs: Optional[DoctorReplacementInput] = None,
                                     skip: Optional[int] = 1,
                                     limit: Optional[int] = 1000,
                                     desc_sorting: Optional[bool] = None) -> DoctorReplacementResult:

        """Получение списка абонементов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorReplacementTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorReplacementResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_subscribe_doctor(self,
                                  info:Info,
                                  filtering_attrs: Optional[SubscribeDoctorInput] = None,
                                  ordering_attrs: Optional[SubscribeDoctorInput] = None,
                                  skip: Optional[int] = 1,
                                  limit: Optional[int] = 1000,
                                  desc_sorting: Optional[bool] = None) -> SubscribeDoctorResult:

        """Получение списка докторов абонементов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, SubscribeDoctorTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return SubscribeDoctorResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_pack_type(self,
                            info:Info,
                            filtering_attrs: Optional[PackTypeInput] = None,
                            ordering_attrs: Optional[PackTypeInput] = None,
                            skip: Optional[int] = 1,
                            limit: Optional[int] = 1000,
                            desc_sorting: Optional[bool] = None) -> PackTypeResult:

        """Получение списка типов пакетов услуг"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, PackTypeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return PackTypeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_subscribe_service_pack(self,
                                         info:Info,
                                         filtering_attrs: Optional[SubscribeServicePackInput] = None,
                                         ordering_attrs: Optional[SubscribeServicePackInput] = None,
                                         skip: Optional[int] = 1,
                                         limit: Optional[int] = 1000,
                                         desc_sorting: Optional[bool] = None) -> SubscribeServicePackResult:

        """Получение списка пакетов услуг абонемента"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, SubscribeServicePackTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return SubscribeServicePackResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_subscribe_spack_record(self,
                                         info:Info,
                                         filtering_attrs: Optional[SubscribeSpackRecordInput] = None,
                                         ordering_attrs: Optional[SubscribeSpackRecordInput] = None,
                                         skip: Optional[int] = 1,
                                         limit: Optional[int] = 1000,
                                         desc_sorting: Optional[bool] = None) -> SubscribeSpackRecordResult:

        """Получение списка пакетов услуг абонемента"""

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        default_obj_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, default_obj_filtering_attrs)

        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        # Фильтруем по пациенту
        if filtering_attrs:
            filtering_attrs.subscribe_services_pack=SubscribeServicePackIn(
                user_subscribe=UserSubscribeIn(
                    policy=PolicyIn(
                        user_id=patient.id
                    )
                )
            )
        else:
            filtering_attrs = SubscribeSpackRecordInput(
                subscribe_services_pack=SubscribeServicePackIn(
                    user_subscribe=UserSubscribeIn(
                        policy=PolicyIn(
                            user_id=patient.id
                        )
                    )
                )
            )

        result_list, records_count, pages_count = await getting_objs(info, user, SubscribeSpackRecordTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return SubscribeSpackRecordResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_shifr_discount_period(self,
                                        info:Info,
                                        filtering_attrs: Optional[ShifrDiscountPeriodInput] = None,
                                        ordering_attrs: Optional[ShifrDiscountPeriodInput] = None,
                                        skip: Optional[int] = 1,
                                        limit: Optional[int] = 1000,
                                        desc_sorting: Optional[bool] = None) -> ShifrDiscountPeriodResult:

        """Получение списка периодов скидок шифров"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, ShifrDiscountPeriodTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return ShifrDiscountPeriodResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_shifr_discount(self,
                                 info:Info,
                                 filtering_attrs: Optional[ShifrDiscountInput] = None,
                                 ordering_attrs: Optional[ShifrDiscountInput] = None,
                                 skip: Optional[int] = 1,
                                 limit: Optional[int] = 1000,
                                 desc_sorting: Optional[bool] = None) -> ShifrDiscountResult:

        """Получение списка скидок по фифрам"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, ShifrDiscountTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return ShifrDiscountResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_service_group(
        self,
        info:Info,
        name: Optional[str] = None
    ) -> ServiceGroupResult:
        """
        Запрос на вывод дерева прейскуранта (чуть доработать)
        """

        result = await getting_service_group1(name)

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_users_purchases(self,
                                  info:Info,
                                  filtering_attrs: Optional[UserPurchaseInput] = None,
                                  ordering_attrs: Optional[UserPurchaseInput] = None,
                                  skip: Optional[int] = 1,
                                  limit: Optional[int] = 1000,
                                  desc_sorting: Optional[bool] = None) -> UserPurchaseResult:

        """Получение корзины пользователя"""

        user, _ = await get_auth_user_by_auth_header(info)

        if filtering_attrs is not None:
            if filtering_attrs.user_id is not None:
                pass
            else:
                filtering_attrs.user_id = user.id
        else:
            filtering_attrs = UserPurchaseInput(
                user_id=user.id
            )

        result_list, records_count, pages_count = await getting_objs(info, user, UserPurchaseTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserPurchaseResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_price_period(self,
                               info:Info,
                               filtering_attrs: Optional[PricePeriodInput] = None,
                               ordering_attrs: Optional[PricePeriodInput] = None,
                               skip: Optional[int] = 1,
                               limit: Optional[int] = 1000,
                               desc_sorting: Optional[bool] = None) -> PricePeriodResult:

        """Получение периодов прайсов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, PricePeriodTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return PricePeriodResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_price_name(self,
                               info:Info,
                               filtering_attrs: Optional[PriceNameInput] = None,
                               ordering_attrs: Optional[PriceNameInput] = None,
                               skip: Optional[int] = 1,
                               limit: Optional[int] = 1000,
                               desc_sorting: Optional[bool] = None) -> PriceNameResult:

        """Получение наименований прайсов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, PriceNameTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return PriceNameResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_price(self,
                        info:Info,
                        filtering_attrs: Optional[PriceInput] = None,
                        ordering_attrs: Optional[PriceInput] = None,
                        skip: Optional[int] = 1,
                        limit: Optional[int] = 1000,
                        desc_sorting: Optional[bool] = None) -> PriceResult:

        """Получение прайсов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, PriceTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return PriceResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_payment_type(self,
                               info:Info,
                               filtering_attrs: Optional[PaymentTypeInput] = None,
                               ordering_attrs: Optional[PaymentTypeInput] = None,
                               skip: Optional[int] = 1,
                               limit: Optional[int] = 1000,
                               desc_sorting: Optional[bool] = None) -> PaymentTypeResult:

        """Получение типов платежей"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, PaymentTypeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return PaymentTypeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_payment(self,
                               info:Info,
                               filtering_attrs: Optional[UserPaymentInput] = None,
                               ordering_attrs: Optional[UserPaymentInput] = None,
                               skip: Optional[int] = 1,
                               limit: Optional[int] = 1000,
                               desc_sorting: Optional[bool] = None) -> UserPaymentResult:

        """Получение платежей пользователя"""

        user, _ = await get_auth_user_by_auth_header(info)

        if filtering_attrs is not None:
            if filtering_attrs.user_id is not None:
                pass
            else:
                filtering_attrs.user_id = user.id
        else:
            filtering_attrs = UserPaymentInput(
                user_id=user.id
            )

        result_list, records_count, pages_count = await getting_objs(info, user, UserPaymentTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserPaymentResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_purchase_return(self,
                                       info:Info,
                                       filtering_attrs: Optional[UserPurchaseReturnInput] = None,
                                       ordering_attrs: Optional[UserPurchaseReturnInput] = None,
                                       skip: Optional[int] = 1,
                                       limit: Optional[int] = 1000,
                                       desc_sorting: Optional[bool] = None) -> UserPurchaseReturnResult:

        """Получение возвратов платежей пользователей"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, UserPurchaseReturnTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserPurchaseReturnResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_refuse_reason(self,
                                info:Info,
                                filtering_attrs: Optional[RefuseReasonInput] = None,
                                ordering_attrs: Optional[RefuseReasonInput] = None,
                                skip: Optional[int] = 1,
                                limit: Optional[int] = 1000,
                                desc_sorting: Optional[bool] = None) -> RefuseReasonResult:

        """Получение причин отказа"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, RefuseReasonTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return RefuseReasonResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_service_plan(self,
                                    info:Info,
                                    filtering_attrs: Optional[UserServicePlanInput] = None,
                                    ordering_attrs: Optional[UserServicePlanInput] = None,
                                    skip: Optional[int] = 1,
                                    limit: Optional[int] = 1000,
                                    desc_sorting: Optional[bool] = None) -> UserServicePlanResult:

        """Получение запланированных услуг пользователей"""

        user, _ = await get_auth_user_by_auth_header(info)

        if filtering_attrs is not None:
            filtering_attrs.user_id = user.id
        else:
            filtering_attrs = UserServicePlanInput(
                user_id=user.id
            )

        result_list, records_count, pages_count = await getting_objs(info, user, UserServicePlanTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserServicePlanResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_access_ticket_all(self,
                                    info:Info,
                                    filtering_attrs: Optional[AccessTicketInput] = None,
                                    ordering_attrs: Optional[AccessTicketInputSort] = None,
                                    skip: Optional[int] = 1,
                                    limit: Optional[int] = 1000,
                                    desc_sorting: Optional[bool] = None) -> AccessTicketResult:

        """Получение номерков"""

        start = time.time()

        today = datetime.today()

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        user_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(
            info, user, UserDefaultObjectTable, user_filtering_attrs
        )
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        result_list, records_count, pages_count = await getting_objs(info, patient, AccessTicketTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return AccessTicketResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok',
            details_ru=today.strftime('%d.%m.%Y %H:%M:%S')
        )

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_access_ticket(self,
                                info:Info,
                                filtering_attrs: Optional[AccessTicketInput] = None,
                                ordering_attrs: Optional[AccessTicketInputSort] = None,
                                skip: Optional[int] = 1,
                                limit: Optional[int] = 1000,
                                desc_sorting: Optional[bool] = None,
                                search: Optional[str] = None) -> AccessTicketResult:

        """Получение номерков"""

        #Временно отключил поиск
        # search = None
        ########################

        start = time.time()

        today = datetime.combine(datetime.today().date(), datetime.min.time()).replace(tzinfo=None)

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        user_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(
            info, user, UserDefaultObjectTable, user_filtering_attrs
        )
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        search_list = []

        if search:
            if search is not None and search != '' and isinstance (search, str):
                search_list = get_search_words(search)

            found_access_tickets_ides = await finding_access_tickets_ides(search_list)

            if filtering_attrs:
                filtering_attrs.id = found_access_tickets_ides
            else:
                filtering_attrs = AccessTicketInput(
                    id=found_access_tickets_ides
                )

        # Отфильтровываем свободные номерки
        if filtering_attrs:
            if not filtering_attrs.user_id:
                filtering_attrs.user_id = [0]
            if not filtering_attrs.doctor_mcenters:
                filtering_attrs.doctor_mcenters = DoctorMedicalCenterIn(
                    medical_center = MedicalCenterIn(
                        show_in_lk = True
                    ),
                    show_in_lk = True
                )
            else:
                if not filtering_attrs.doctor_mcenters.medical_center:
                    filtering_attrs.doctor_mcenters.medical_center = MedicalCenterIn(
                        show_in_lk = True
                    )
        else:
            filtering_attrs = AccessTicketInput(
                user_id = [0],
                doctor_mcenters = DoctorMedicalCenterIn(
                    medical_center = MedicalCenterIn()
                )
            )
            filtering_attrs.doctor_mcenters.medical_center.show_in_lk = True
            filtering_attrs.doctor_mcenters.show_in_lk = True

        filtering_attrs.bl_status = 1
        filtering_attrs.is_active = True

        result_list, records_count, pages_count = await getting_objs(info, patient, AccessTicketTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        end1 = time.time()
        print(f'Затрачено времени на запрос в БД {(end1-start)*1000} мс')

        # Отсекаем просроченные
        result_list = [x for x in result_list if x.ticket_datetime >= today]

        dates_set = set([str(x.ticket_datetime.date()) for x in result_list])
        dates_list = sorted(list(dates_set), key=lambda x: x)

        doctor_mcenter_set = set([x.doctor_mcenters for x in result_list])
        doctor_mcenter_list = sorted(list(doctor_mcenter_set), key=lambda x: x.doctor.last_name)

        medical_speciality_set = set([x.doctor_mcenters.medical_speciality for x in result_list])
        medical_speciality_list = sorted(list(medical_speciality_set), key=lambda x: x.view_name)

        for item in medical_speciality_list:
            item.doctor_mcenter_list = []
            for doctor in doctor_mcenter_list:
                if item.id == doctor.medical_speciality_id:
                    item.doctor_mcenter_list.append(doctor)
            item.doctor_mcenter_list = sorted(item.doctor_mcenter_list, key=lambda x: x.doctor.last_name)

        medical_position_set = set([x.doctor_mcenters.medical_position for x in result_list])
        medical_position_list = sorted(list(medical_position_set), key=lambda x: x.view_name)

        for item in medical_position_list:
            item.doctor_mcenter_list = []
            for doctor in doctor_mcenter_list:
                if item.id == doctor.medical_position_id:
                    item.doctor_mcenter_list.append(doctor)
            item.doctor_mcenter_list = sorted(item.doctor_mcenter_list, key=lambda x: x.doctor.last_name)

        medical_centers_set = set([x.doctor_mcenters.medical_center for x in result_list])
        medical_centers_list = sorted(list(medical_centers_set), key=lambda x: x.name)

        doctor_mcenter_ides = [x.id for x in doctor_mcenter_list]
        medical_centers_ides = [x.id for x in medical_centers_list]

        doctor_services_list = await getting_services_with_price(info, patient, doctor_mcenter_ides,
                                                                 medical_centers_ides, search_list)

        service_group_with_services_list = await getting_service_group3(doctor_services_list)

        end2 = time.time()
        print(f'Затрачено времени на подготовку справочных списков {(end2-end1)*1000} мс')
        print(f'Полное время на выполнение процедуры {(end2-start)*1000} мс')

        return AccessTicketResult(
            data=result_list,
            dates_list=dates_list,
            medical_centers_list=medical_centers_list,
            medical_speciality_list=medical_speciality_list,
            medical_position_list=medical_position_list,
            doctor_mcenter_list=doctor_mcenter_list,
            service_group_with_services_list=service_group_with_services_list.data,
            services_plain_list=doctor_services_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def get_doctor_mcenter_services(self,
                                          info:Info,
                                          filtering_attrs: Optional[DoctorMedicalCenterServiceInput] = None,
                                          ordering_attrs: Optional[DoctorMedicalCenterServiceInput] = None,
                                          skip: Optional[int] = 1,
                                          limit: Optional[int] = 1000,
                                          desc_sorting: Optional[bool] = None) -> DoctorMedicalCenterServiceResult:

        """Получение услуг докторов в медцентрах"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, DoctorMedicalCenterServiceTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return DoctorMedicalCenterServiceResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_service_group_with_services(
        self,
        info:Info,
        services_ides: Optional[List[int]] = None
    ) -> ServiceGroupResult:
        """
        Запрос на вывод дерева прейскуранта с услугами
        """

        result = await getting_service_group2(services_ides)

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_mcenters_price_names(self,
                                       info:Info,
                                       filtering_attrs: Optional[MedicalCenterPriceNameInput] = None,
                                       ordering_attrs: Optional[MedicalCenterPriceNameInput] = None,
                                       skip: Optional[int] = 1,
                                       limit: Optional[int] = 1000,
                                       desc_sorting: Optional[bool] = None) -> MedicalCenterPriceNameResult:

        """Получение причин отказа"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, MedicalCenterPriceNameTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return MedicalCenterPriceNameResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_default_objects(self,
                                       info:Info,
                                       filtering_attrs: Optional[UserDefaultObjectInput] = None,
                                       ordering_attrs: Optional[UserDefaultObjectInput] = None,
                                       skip: Optional[int] = 1,
                                       limit: Optional[int] = 1000,
                                       desc_sorting: Optional[bool] = None) -> UserDefaultObjectResult:

        """Получение объектов по умолчанию пользователя"""

        user, _ = await get_auth_user_by_auth_header(info)

        if filtering_attrs is not None:
            filtering_attrs.user_id = user.id
        else:
            filtering_attrs = UserDefaultObjectInput(
                user_id=user.id
            )

        result_list, records_count, pages_count = await getting_objs(info, user, UserDefaultObjectTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserDefaultObjectResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_subscribe_info_blocks(self,
                                        info:Info,
                                        subscribe_id: int,
                                        ) -> SubscribeInfoBlocksResult:
        """Получение информационных блоков по абонементу"""

        #Получаем пациента по умолчанию
        user, _ = await get_auth_user_by_auth_header(info)

        filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, filtering_attrs)
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        result_list = await getting_subscribe_info_blocks(info, patient, subscribe_id)

        return result_list

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_events_calendar(self,
                                        info:Info,
                                        start_date: str,
                                        end_date: str,
                                        patient_ids: Optional[List[int]] = None
                                        ) -> EventsCalendarResult:
        """Получение календаря событий"""

        user, _ = await get_auth_user_by_auth_header(info)

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(hours=23, minutes=59)
            except Exception as e:
                print(e)
                return EventsCalendarResult(
                    details="The fields 'start_date' or 'end_date' or both are wrong. The right format is 'YYYY-MM-DD'.",
                    details_ru="Поля start_date или end_date или оба имеют ошибочный формат. Правильный формат 'YYYY-MM-DD'.",
                    status_code=422
                )
        else:
            return EventsCalendarResult(
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
                    return EventsCalendarResult(
                        status_code=422,
                        details=f'The patient with number {person} is not your relatives',
                        details_ru=f'Пациент с номером {person} не является вашим родственником'
                    )

        result_list = await getting_events_calendar(info, start_date, end_date, patient_ids)

        return EventsCalendarResult(
            data=result_list,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_visits_history(self,
                                 info:Info,
                                 start_date: str,
                                 end_date: str,
                                 patient_ids: Optional[List[int]] = None
                                 ) -> VisitHistoryRecordResult:
        """Получение истории посещений"""

        user, _ = await get_auth_user_by_auth_header(info)

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(hours=23, minutes=59)
            except Exception as e:
                print(e)
                return VisitHistoryRecordResult(
                    details="The fields 'start_date' or 'end_date' or both are wrong. The right format is 'YYYY-MM-DD'.",
                    details_ru="Поля start_date или end_date или оба имеют ошибочный формат. Правильный формат 'YYYY-MM-DD'.",
                    status_code=422
                )
            if (end_date - start_date) > timedelta(days=366):
                return VisitHistoryRecordResult(
                    details="The interval between the 'start_date' and 'end_date' mustn't more than 1 year.",
                    details_ru="Интервал времени между start_date и end_date не должен превышать 1 года.",
                    status_code=422
                )
        else:
            return VisitHistoryRecordResult(
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
                    return VisitHistoryRecordResult(
                        status_code=422,
                        details=f'The patient with number {person} is not your relatives',
                        details_ru=f'Пациент с номером {person} не является вашим родственником'
                    )

        result_list = await getting_visits_history(info, start_date, end_date, patient_ids)

        return VisitHistoryRecordResult(
            data=result_list,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )
