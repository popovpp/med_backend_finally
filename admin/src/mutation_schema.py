import strawberry
from strawberry.types import Info
from typing import Optional
# from kafka import KafkaProducer

from core.authorization.permissions import IsAdmin, IsAuthenticated
from core.config.scalars import RequestResult
from core.sa_tables.main_process import (ServiceTypeTable, MedicalPositionTable,
                                         ServiceTable, MedicalSpecialityTable, DoctorTable, DoctorMspecialityTable,
                                         StaffTypeTable, DoctorCategoryTable, DoctorStatusTypeTable, DoctorStatusTable,
                                         PatientTypeTable, DoctorMedicalCenterTable, DoctorPatientTypeTable,
                                         ServiceMedicalSpecialityTable, ComplexServiceTable, ComplexServiceItemTable,
                                         FinancialTypeTable, ShifrTable, PolicyTable, UserSubscribeTable,
                                         DoctorReplacementTable, SubscribeDoctorTable, PackTypeTable,
                                         SubscribeServicePackTable, SubscribeSpackRecordTable, ShifrDiscountPeriodTable,
                                         ShifrDiscountTable, PricePeriodTable, PriceNameTable, PriceTable,
                                         PaymentTypeTable, UserPaymentTable, UserPurchaseReturnTable, RefuseReasonTable,
                                         UserServiceCartTable, UserServicePlanTable, AccessTicketTable,
                                         DoctorMedicalCenterServiceTable, MedicalCenterPriceNameTable,
                                         UserDefaultObjectTable)
from core.sa_tables.accounts import CityTable, MedicalCenterTable, RelationshipDegreesTable, UserRelativeTable
from core.sa_tables.admin import UserAdminTable
from core.src.common_resolvers import adding_updating_obj, deleting_obj
from .scalars import (CityInputAdm, MedicalCenterInputAdm, ServiceTypeInputAdm, MedicalPositionInputAdm, ServiceInputAdm,
                      MedicalSpecialityInputAdm, DoctorInputAdm, DoctorMspecialityInputAdm, StaffTypeInputAdm,
                      DoctorCategoryInputAdm, DoctorStatusTypeInputAdm, DoctorStatusInputAdm, PatientTypeInputAdm,
                      DoctorMedicalCenterInputAdm, DoctorPatientTypeInputAdm, ServiceMedicalSpecialityInputAdm,
                      ComplexServiceInputAdm, ComplexServiceItemInputAdm, FinancialTypeInputAdm, ShifrInputAdm,
                      PolicyInputAdm, UserSubscribeInputAdm, DoctorReplacementInputAdm, SubscribeDoctorInputAdm,
                      PackTypeInputAdm, SubscribeServicePackInputAdm, SubscribeSpackRecordInputAdm, ShifrDiscountPeriodInputAdm,
                      ShifrDiscountInputAdm, PricePeriodInputAdm, PriceNameInputAdm, PriceInputAdm, PaymentTypeInputAdm,
                      UserPaymentInputAdm, UserPurchaseReturnInputAdm, RefuseReasonInputAdm, UserServiceCartInputAdm,
                      UserServicePlanInputAdm, AccessTicketInputAdm, RelationshipDegreesInputAdm,
                      UserRelativeInputAdm, DoctorMedicalCenterServiceInputAdm, MedicalCenterPriceNameInputAdm,
                      UserDefaultObjectInputAdm, UserAdminInputAdm)
from .resolvers import guest_registrating


@strawberry.type
class MutationAdmin:

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def guest_registration(
        self,
        info: Info
    ) -> RequestResult:
        """Регистрация пользователя guest"""

        result = await guest_registrating()

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_city(
        self,
        info:Info,
        city: CityInputAdm,
        city_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление редактирование города
        """

        result = await adding_updating_obj(city, CityTable, city_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_city(
        self,
        info:Info,
        city_id: int
    ) -> RequestResult:
        """
        Запрос на удаление города
        """

        result = await deleting_obj(city_id, CityTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_medical_center(
        self,
        info:Info,
        medical_center: MedicalCenterInputAdm,
        medical_center_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование медицинского центра
        """

        result = await adding_updating_obj(medical_center, MedicalCenterTable, medical_center_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_medical_center(
        self,
        info:Info,
        medical_center_id: int
    ) -> RequestResult:
        """
        Запрос на удаление медицинского центра
        """

        result = await deleting_obj(medical_center_id, MedicalCenterTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_service_type(
        self,
        info: Info,
        service_type: ServiceTypeInputAdm,
        service_type_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование типа медицинскоих услуг
        """

        result = await adding_updating_obj(service_type, ServiceTypeTable, service_type_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_service_type(
        self,
        info: Info,
        service_type_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи из таблицы типа медицинских услуг
        """

        result = await deleting_obj(service_type_id, ServiceTypeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_medical_position(
        self,
        info: Info,
        medical_position: MedicalPositionInputAdm,
        medical_position_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование медицинских должностей
        """

        result = await adding_updating_obj(medical_position, MedicalPositionTable, medical_position_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_medical_position(
        self,
        info: Info,
        medical_position_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи из таблицы медицинских должностей
        """

        result = await deleting_obj(medical_position_id, MedicalPositionTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_sevice(
        self,
        info: Info,
        service: ServiceInputAdm,
        service_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование услуги
        """

        result = await adding_updating_obj(service, ServiceTable, service_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_service(
        self,
        info: Info,
        service_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи из таблицы медицинских услуг
        """

        result = await deleting_obj(service_id, ServiceTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_medical_speciality(
        self,
        info: Info,
        medical_speciality: MedicalSpecialityInputAdm,
        medical_speciality_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование медицинской специальности
        """

        result = await adding_updating_obj(medical_speciality, MedicalSpecialityTable, medical_speciality_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_medical_speciality(
        self,
        info: Info,
        medical_speciality_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи из таблицы медицинских специальностей
        """

        result = await deleting_obj(medical_speciality_id, MedicalSpecialityTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor(
        self,
        info: Info,
        doctor: DoctorInputAdm,
        doctor_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование доктора
        """

        result = await adding_updating_obj(doctor, DoctorTable, doctor_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor(
        self,
        info: Info,
        doctor_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи доктора
        """

        result = await deleting_obj(doctor_id, DoctorTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor_mspecialities(
        self,
        info: Info,
        doctor_mspeciality: DoctorMspecialityInputAdm,
        doctor_mspeciality_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование доктора
        """

        result = await adding_updating_obj(doctor_mspeciality, DoctorMspecialityTable, doctor_mspeciality_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor_mspeciality(
        self,
        info: Info,
        doctor_mspeciality_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи доктора
        """

        result = await deleting_obj(doctor_mspeciality_id, DoctorMspecialityTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_staff_type(
        self,
        info: Info,
        staff_type: StaffTypeInputAdm,
        staff_type_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование типа персонала
        """

        result = await adding_updating_obj(staff_type, StaffTypeTable, staff_type_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_staff_type(
        self,
        info: Info,
        staff_type_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи типв персонала
        """

        result = await deleting_obj(staff_type_id, StaffTypeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor_category(
        self,
        info: Info,
        doctor_category: DoctorCategoryInputAdm,
        doctor_category_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование категории доктора
        """

        result = await adding_updating_obj(doctor_category, DoctorCategoryTable, doctor_category_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor_category(
        self,
        info: Info,
        doctor_category_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи категории доктора
        """

        result = await deleting_obj(doctor_category_id, DoctorCategoryTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor_status_type(
        self,
        info: Info,
        doctor_status_type: DoctorStatusTypeInputAdm,
        doctor_status_type_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование типа статуса доктора
        """

        result = await adding_updating_obj(doctor_status_type, DoctorStatusTypeTable, doctor_status_type_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor_status_type(
        self,
        info: Info,
        doctor_status_type_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи типа статуса доктора
        """

        result = await deleting_obj(doctor_status_type_id, DoctorStatusTypeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor_status(
        self,
        info: Info,
        doctor_status: DoctorStatusInputAdm,
        doctor_status_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование статуса доктора
        """

        result = await adding_updating_obj(doctor_status, DoctorStatusTable, doctor_status_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor_status(
        self,
        info: Info,
        doctor_status_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи статуса доктора
        """

        result = await deleting_obj(doctor_status_id, DoctorStatusTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_patient_type(
        self,
        info: Info,
        patient_type: PatientTypeInputAdm,
        patient_type_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование статуса пациетов
        """

        result = await adding_updating_obj(patient_type, PatientTypeTable, patient_type_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_patient_type(
        self,
        info: Info,
        patient_type_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи статуса пациентов
        """

        result = await deleting_obj(patient_type_id, PatientTypeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor_medical_center(
        self,
        info: Info,
        doctor_medical_center: DoctorMedicalCenterInputAdm,
        doctor_medical_center_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование статуса пациетов
        """

        result = await adding_updating_obj(doctor_medical_center, DoctorMedicalCenterTable, doctor_medical_center_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor_medical_center(
        self,
        info: Info,
        doctor_medical_center_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи статуса пациентов
        """

        result = await deleting_obj(doctor_medical_center_id, DoctorMedicalCenterTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor_patient_type(
        self,
        info: Info,
        doctor_patient_type: DoctorPatientTypeInputAdm,
        doctor_patient_type_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование типа пациета доктора
        """

        result = await adding_updating_obj(doctor_patient_type, DoctorPatientTypeTable, doctor_patient_type_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor_patient_type(
        self,
        info: Info,
        doctor_patient_type_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи типа пациента доктора
        """

        result = await deleting_obj(doctor_patient_type_id, DoctorPatientTypeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_service_medical_speciality(
        self,
        info: Info,
        service_medical_speciality: ServiceMedicalSpecialityInputAdm,
        service_medical_speciality_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование медицинской специальности услуги
        """

        result = await adding_updating_obj(service_medical_speciality, ServiceMedicalSpecialityTable,
                                           service_medical_speciality_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_service_medical_speciality(
        self,
        info: Info,
        service_medical_speciality_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи медицинской специальности услуги
        """

        result = await deleting_obj(service_medical_speciality_id, ServiceMedicalSpecialityTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_complex_service(
        self,
        info: Info,
        complex_service: ComplexServiceInputAdm,
        complex_service_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование комплексной услуги
        """

        result = await adding_updating_obj(complex_service, ComplexServiceTable,
                                           complex_service_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_complex_service(
        self,
        info: Info,
        complex_service_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи комплексной услуги
        """

        result = await deleting_obj(complex_service_id, ComplexServiceTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_complex_service_item(
        self,
        info: Info,
        complex_service_item: ComplexServiceItemInputAdm,
        complex_service_item_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование элемента комплексной услуги
        """

        result = await adding_updating_obj(complex_service_item, ComplexServiceItemTable,
                                           complex_service_item_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_complex_service_item(
        self,
        info: Info,
        complex_service_item_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи элемента комплексной услуги
        """

        result = await deleting_obj(complex_service_item_id, ComplexServiceItemTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_financial_type(
        self,
        info: Info,
        financial_type: FinancialTypeInputAdm,
        financial_type_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование финансового типа
        """

        result = await adding_updating_obj(financial_type, FinancialTypeTable,
                                           financial_type_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_financial_type(
        self,
        info: Info,
        financial_type_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи финансового типа
        """

        result = await deleting_obj(financial_type_id, FinancialTypeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_shifr(
                               self,
                               info: Info,
                               shifr: ShifrInputAdm,
                               shifr_id: Optional[int] = None
                              ) -> RequestResult:
        """
        Запрос на добавление и редактирование шифра
        """

        result = await adding_updating_obj(shifr, ShifrTable,
                                           shifr_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_shifr(
        self,
        info: Info,
        shifr_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи шифра
        """

        result = await deleting_obj(shifr_id, ShifrTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_policy(
                               self,
                               info: Info,
                               policy: PolicyInputAdm,
                               policy_id: Optional[int] = None
                              ) -> RequestResult:
        """
        Запрос на добавление и редактирование полиса
        """

        result = await adding_updating_obj(policy, PolicyTable,
                                           policy_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_policy(
        self,
        info: Info,
        policy_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи полиса
        """

        result = await deleting_obj(policy_id, PolicyTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_user_suscribe(
                                       self,
                                       info: Info,
                                       user_subscribe: UserSubscribeInputAdm,
                                       user_subscribe_id: Optional[int] = None
                                       ) -> RequestResult:
        """
        Запрос на добавление и редактирование абонемента пользователя
        """

        result = await adding_updating_obj(user_subscribe, UserSubscribeTable,
                                           user_subscribe_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_user_subscribe(
        self,
        info: Info,
        user_subscribe_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи абонемента пользователя
        """

        result = await deleting_obj(user_subscribe_id, UserSubscribeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor_replacement(
                                            self,
                                            info: Info,
                                            doctor_replacement: DoctorReplacementInputAdm,
                                            doctor_replacement_id: Optional[int] = None
                                            ) -> RequestResult:
        """
        Запрос на добавление и редактирование замен ы доктора
        """

        result = await adding_updating_obj(doctor_replacement, DoctorReplacementTable,
                                           doctor_replacement_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor_replacement(
        self,
        info: Info,
        doctor_replacement_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи замены доктора
        """

        result = await deleting_obj(doctor_replacement_id, DoctorReplacementTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_subscribe_doctor(
                                          self,
                                          info: Info,
                                          subscribe_doctor: SubscribeDoctorInputAdm,
                                          subscribe_doctor_id: Optional[int] = None
                                          ) -> RequestResult:
        """
        Запрос на добавление и редактирование доктора на абонементе
        """

        result = await adding_updating_obj(subscribe_doctor, SubscribeDoctorTable,
                                           subscribe_doctor_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_subscribe_doctor(
        self,
        info: Info,
        subscribe_doctor_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи замены доктора
        """

        result = await deleting_obj(subscribe_doctor_id, SubscribeDoctorTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_pack_type(
                                   self,
                                   info: Info,
                                   pack_type: PackTypeInputAdm,
                                   pack_type_id: Optional[int] = None
                                   ) -> RequestResult:
        """
        Запрос на добавление и редактирование доктора на абонементе
        """

        result = await adding_updating_obj(pack_type, PackTypeTable,
                                           pack_type_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_pack_type(
        self,
        info: Info,
        pack_type_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи типа пакета услуг
        """

        result = await deleting_obj(pack_type_id, PackTypeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_subscribe_service_pack(
                                                self,
                                                info: Info,
                                                subscribe_service_pack: SubscribeServicePackInputAdm,
                                                subscribe_service_pack_id: Optional[int] = None
                                                ) -> RequestResult:
        """
        Запрос на добавление и редактирование пакета услуг в абонемент
        """

        result = await adding_updating_obj(subscribe_service_pack, SubscribeServicePackTable,
                                           subscribe_service_pack_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_subscribe_service_pack(
        self,
        info: Info,
        subscribe_service_pack_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи пакета услуг в абонементе
        """

        result = await deleting_obj(subscribe_service_pack_id, SubscribeServicePackTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_subscribe_spack_record(
                                                self,
                                                info: Info,
                                                subscribe_spack_record: SubscribeSpackRecordInputAdm,
                                                subscribe_spack_record_id: Optional[int] = None
                                                ) -> RequestResult:
        """
        Запрос на добавление и редактирование записи в пакете услуг в абонемент
        """

        result = await adding_updating_obj(subscribe_spack_record, SubscribeSpackRecordTable,
                                           subscribe_spack_record_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_subscribe_spack_record(
        self,
        info: Info,
        subscribe_spack_record_id: int
    ) -> RequestResult:
        """
        Запрос на удаление записи пакета услуг в абонементе
        """

        result = await deleting_obj(subscribe_spack_record_id, SubscribeSpackRecordTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_shifr_discouont_period(
                                                self,
                                                info: Info,
                                                shifr_discount_period: ShifrDiscountPeriodInputAdm,
                                                shifr_discount_period_id: Optional[int] = None
                                                ) -> RequestResult:
        """
        Запрос на добавление и редактирование периода скидок шифра
        """

        result = await adding_updating_obj(shifr_discount_period, ShifrDiscountPeriodTable,
                                           shifr_discount_period_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_shifr_discouont_period(
        self,
        info: Info,
        shifr_discouont_period_id: int
    ) -> RequestResult:
        """
        Запрос на удаление периода шифра скидок
        """

        result = await deleting_obj(shifr_discouont_period_id, ShifrDiscountPeriodTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_shifr_discouont(
                                         self,
                                         info: Info,
                                         shifr_discount: ShifrDiscountInputAdm,
                                         shifr_discount_id: Optional[int] = None
                                         ) -> RequestResult:
        """
        Запрос на добавление и редактирование скидок шифра
        """

        result = await adding_updating_obj(shifr_discount, ShifrDiscountTable,
                                           shifr_discount_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_shifr_discouont(
        self,
        info: Info,
        shifr_discouont_id: int
    ) -> RequestResult:
        """
        Запрос на удаление скидки шифра
        """

        result = await deleting_obj(shifr_discouont_id, ShifrDiscountTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_price_period(
                                      self,
                                      info: Info,
                                      price_period: PricePeriodInputAdm,
                                      price_period_id: Optional[int] = None
                                     ) -> RequestResult:
        """
        Запрос на добавление и редактирование периода прайса
        """

        result = await adding_updating_obj(price_period, PricePeriodTable,
                                           price_period_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_price_period(
        self,
        info: Info,
        price_period_id: int
    ) -> RequestResult:
        """
        Запрос на удаление периода прайса
        """

        result = await deleting_obj(price_period_id, PricePeriodTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_price_name(
                                    self,
                                    info: Info,
                                    price_name: PriceNameInputAdm,
                                    price_name_id: Optional[int] = None
                                    ) -> RequestResult:
        """
        Запрос на добавление и редактирование наименования прайса
        """

        result = await adding_updating_obj(price_name, PriceNameTable,
                                           price_name_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_price_name(
        self,
        info: Info,
        price_name_id: int
    ) -> RequestResult:
        """
        Запрос на удаление периода прайса
        """

        result = await deleting_obj(price_name_id, PriceNameTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_price(
                               self,
                               info: Info,
                               price: PriceInputAdm,
                               price_id: Optional[int] = None
                               ) -> RequestResult:
        """
        Запрос на добавление и редактирование наименования прайса
        """

        result = await adding_updating_obj(price, PriceTable,
                                           price_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_price(
        self,
        info: Info,
        price_id: int
    ) -> RequestResult:
        """
        Запрос на удаление периода прайса
        """

        result = await deleting_obj(price_id, PriceTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_payment_type(
                                      self,
                                      info: Info,
                                      payment_type: PaymentTypeInputAdm,
                                      payment_type_id: Optional[int] = None
                                      ) -> RequestResult:
        """
        Запрос на добавление и редактирование типа платежа
        """

        result = await adding_updating_obj(payment_type, PaymentTypeTable,
                                           payment_type_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_payment_type(
        self,
        info: Info,
        payment_type_id: int
    ) -> RequestResult:
        """
        Запрос на удаление типа платежа
        """

        result = await deleting_obj(payment_type_id, PaymentTypeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_user_payment(
                               self,
                               info: Info,
                               user_payment: UserPaymentInputAdm,
                               user_payment_id: Optional[int] = None
                               ) -> RequestResult:
        """
        Запрос на добавление и редактирование платежа пользователя
        """

        result = await adding_updating_obj(user_payment, UserPaymentTable,
                                           user_payment_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_user_payment(
        self,
        info: Info,
        user_payment_id: int
    ) -> RequestResult:
        """
        Запрос на удаление типа платежа
        """

        result = await deleting_obj(user_payment_id, UserPaymentTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_user_purchase_return(
                                       self,
                                       info: Info,
                                       user_purchase_return: UserPurchaseReturnInputAdm,
                                       user_purchase_return_id: Optional[int] = None
                                       ) -> RequestResult:
        """
        Запрос на добавление и редактирование возврата платежа пользователя
        """

        result = await adding_updating_obj(user_purchase_return, UserPurchaseReturnTable,
                                           user_purchase_return_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_user_purchase_return(
        self,
        info: Info,
        user_purchase_return_id: int
    ) -> RequestResult:
        """
        Запрос на удаление возврата платежа
        """

        result = await deleting_obj(user_purchase_return_id, UserPurchaseReturnTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_refuse_reason(
                                       self,
                                       info: Info,
                                       refuse_reason: RefuseReasonInputAdm,
                                       refuse_reason_id: Optional[int] = None
                                       ) -> RequestResult:
        """
        Запрос на добавление и редактирование причины отказа
        """

        result = await adding_updating_obj(refuse_reason, RefuseReasonTable,
                                           refuse_reason_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_refuse_reason(
        self,
        info: Info,
        refuse_reason_id: int
    ) -> RequestResult:
        """
        Запрос на удаление причины отказа
        """

        result = await deleting_obj(refuse_reason_id, RefuseReasonTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_user_service_cart(
                                           self,
                                           info: Info,
                                           user_service_cart: UserServiceCartInputAdm,
                                           user_service_cart_id: Optional[int] = None
                                           ) -> RequestResult:
        """
        Запрос на добавление и редактирование корзины пользователя
        """

        result = await adding_updating_obj(user_service_cart, UserServiceCartTable,
                                           user_service_cart_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_user_service_cart(
        self,
        info: Info,
        user_service_cart_id: int
    ) -> RequestResult:
        """
        Запрос на удаление корзины пользователя
        """

        result = await deleting_obj(user_service_cart_id, UserServiceCartTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_user_service_plan(
                                           self,
                                           info: Info,
                                           user_service_plan: UserServicePlanInputAdm,
                                           user_service_plan_id: Optional[int] = None
                                           ) -> RequestResult:
        """
        Запрос на добавление и редактирование запланированных услуг пользователя
        """

        result = await adding_updating_obj(user_service_plan, UserServicePlanTable,
                                           user_service_plan_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_user_service_plan(
        self,
        info: Info,
        user_service_plan_id: int
    ) -> RequestResult:
        """
        Запрос на удаление запланированныз услуг пользователя
        """

        result = await deleting_obj(user_service_plan_id, UserServicePlanTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_access_ticket(
                                       self,
                                       info: Info,
                                       access_ticket: AccessTicketInputAdm,
                                       access_ticket_id: Optional[int] = None
                                       ) -> RequestResult:
        """
        Запрос на добавление и редактирование номерков
        """

        result = await adding_updating_obj(access_ticket, AccessTicketTable,
                                           access_ticket_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_access_ticket(
        self,
        info: Info,
        access_ticket_id: int
    ) -> RequestResult:
        """
        Запрос на удаление номерков
        """

        result = await deleting_obj(access_ticket_id, AccessTicketTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_relationship_degrees(
                                       self,
                                       info: Info,
                                       relationship_degrees: RelationshipDegreesInputAdm,
                                       relationship_degrees_id: Optional[int] = None
                                       ) -> RequestResult:
        """
        Запрос на добавление и редактирование степени родства
        """

        result = await adding_updating_obj(relationship_degrees, RelationshipDegreesTable,
                                           relationship_degrees_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_relationship_degrees(
        self,
        info: Info,
        relationship_degrees_id: int
    ) -> RequestResult:
        """
        Запрос на удаление степени родства
        """

        result = await deleting_obj(relationship_degrees_id, RelationshipDegreesTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_user_relative(
                                       self,
                                       info: Info,
                                       user_relative: UserRelativeInputAdm,
                                       user_relative_id: Optional[int] = None
                                       ) -> RequestResult:
        """
        Запрос на добавление и редактирование родственника пользователя
        """

        result = await adding_updating_obj(user_relative, UserRelativeTable,
                                           user_relative_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_user_relative(
        self,
        info: Info,
        user_relative_id: int
    ) -> RequestResult:
        """
        Запрос на удаление родственника пользователя
        """

        result = await deleting_obj(user_relative_id, UserRelativeTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_doctor_mcenter_service(
                                                self,
                                                info: Info,
                                                doctor_mcenter_service: DoctorMedicalCenterServiceInputAdm,
                                                doctor_mcenter_service_id: Optional[int] = None
                                                ) -> RequestResult:
        """
        Запрос на добавление и редактирование услуги доктора в медцентре
        """

        result = await adding_updating_obj(doctor_mcenter_service, DoctorMedicalCenterServiceTable,
                                           doctor_mcenter_service_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_doctor_mcenter_service(
        self,
        info: Info,
        doctor_mcenter_service_id: int
    ) -> RequestResult:
        """
        Запрос на удаление услуги доктора в медцентре
        """

        result = await deleting_obj(doctor_mcenter_service_id, DoctorMedicalCenterServiceTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_mcenter_price_name(
                                            self,
                                            info: Info,
                                            mcenter_price_name: MedicalCenterPriceNameInputAdm,
                                            mcenter_price_name_id: Optional[int] = None
                                            ) -> RequestResult:
        """
        Запрос на добавление и редактирование имен прайсов в медцентрах
        """

        result = await adding_updating_obj(mcenter_price_name, MedicalCenterPriceNameTable,
                                           mcenter_price_name_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def delete_mcenter_price_name(
        self,
        info: Info,
        mcenter_price_name_id: int
    ) -> RequestResult:
        """
        Запрос на удаление имени прайса в медцентре
        """

        result = await deleting_obj(mcenter_price_name_id, MedicalCenterPriceNameTable)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_user_default_objects(
                                              self,
                                              info: Info,
                                              user_default_objects: UserDefaultObjectInputAdm,
                                              user_default_objects_id: Optional[int] = None
                                              ) -> RequestResult:
        """
        Запрос на добавление и редактирование объектов пользователя по умолчанию
        """

        result = await adding_updating_obj(user_default_objects, UserDefaultObjectTable,
                                           user_default_objects_id)

        return result

    @strawberry.field(permission_classes=[IsAdmin])
    async def add_update_user_admin_info(
        self,
        info:Info,
        user_admin_info: UserAdminInputAdm,
        user_admin_info_id: Optional[int] = None
    ) -> RequestResult:
        """
        Запрос на добавление и редактирование админской инфы пользователя
        """

        result = await adding_updating_obj(user_admin_info, UserAdminTable, user_admin_info_id)

        return result
