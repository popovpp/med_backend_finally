import strawberry
from datetime import datetime, date
from typing import Optional, List

from core.config.mapped_scalars import (MedicalCenter, City, ServiceType, User,
                                        Service, MedicalSpeciality, Doctor, DoctorMspeciality,
                                        ServiceGroup, MedicalPosition, StaffType, DoctorCategory,
                                        DoctorStatusType, DoctorStatus, PatientType, DoctorMedicalCenter, DoctorPatientType,
                                        ServiceMedicalSpeciality, ComplexService, ComplexServiceItem, FinancialType,
                                        Shifr, Policy, UserSubscribe, DoctorReplacement, SubscribeDoctor,
                                        PackType, SubscribeServicePack, SubscribeSpackRecord, ShifrDiscountPeriod,
                                        ShifrDiscount, UserPurchase, PricePeriod, PriceName, Price, PaymentType,
                                        UserPayment, UserPurchaseReturn, RefuseReason, UserServicePlan,
                                        AccessTicket, DoctorMedicalCenterService, MedicalCenterPriceName, UserDefaultObject)
from core.config.scalars import (RequestResult, MedicalCenterIn, ServiceTypeIn, CityIn, ServiceDirectionIn,
                                 ServiceIn, MedicalSpecialityIn, DoctorIn, DoctorMspecialityIn, DoctorServiceIn,
                                 PriceIn, IntFilteringInterval, DoctorScheduleIn, DateTimeFilteringInterval,
                                 ServiceGroupIn, DoctorCategoryIn, MedicalPositionIn, StaffTypeIn, DoctorStatusTypeIn,
                                 DoctorStatusIn, PatientTypeIn, DoctorMedicalCenterIn, DoctorPatientTypeIn,
                                 ServiceMedicalSpecialityIn, ComplexServiceIn, ComplexServiceItemIn, FinancialTypeIn,
                                 ShifrIn, PolicyIn, UserIn, UserSubscribeIn, DoctorReplacementIn, SubscribeDoctorIn,
                                 PackTypeIn, SubscribeServicePackIn, SubscribeSpackRecordIn, ShifrDiscountPeriodIn,
                                 ShifrDiscountIn, UserPurchaseIn, PricePeriodIn, PriceNameIn, PaymentTypeIn,
                                 UserPaymentIn, UserPurchaseReturnIn, RefuseReasonIn,UserServiceCartIn,
                                 AccessTicketIn, UserServicePlanIn, DoctorMedicalCenterServiceIn, MedicalCenterPriceNameIn,
                                 UserDefaultObjectIn, PolicyPaymentPlanIn, PayKeeperPaymentDataIn)


@strawberry.type
class MedicalCenterResult(RequestResult):
    data: Optional[List[MedicalCenter]]


@strawberry.type
class CityResult(RequestResult):
    data: Optional[List[City]]


@strawberry.type
class ServiceDirectionResult(RequestResult):
    data: Optional[List[str]]


@strawberry.type
class ServiceTypeResult(RequestResult):
    data: Optional[List[ServiceType]]


@strawberry.type
class ServiceResult(RequestResult):
    data: Optional[List[Service]]


@strawberry.type
class MedicalSpecialityResult(RequestResult):
    data: Optional[List[MedicalSpeciality]]


@strawberry.type
class DoctorResult(RequestResult):
    data: Optional[List[Doctor]]


@strawberry.type
class DoctorMspecialityResult(RequestResult):
    data: Optional[List[DoctorMspeciality]]


@strawberry.type
class DoctorServiceResult(RequestResult):
    data: Optional[List[str]]


@strawberry.type
class PriceResult(RequestResult):
    data: Optional[List[Price]]


@strawberry.type
class ServiceGroupResult(RequestResult):
    data: Optional[List[ServiceGroup]]


@strawberry.type
class DoctorScheduleDate:
    date: str
    schedule: Optional[List[str]]


@strawberry.type
class DoctorScheduleResult(RequestResult):
    data: Optional[List[DoctorScheduleDate]]


@strawberry.type
class MedicalPositionResult(RequestResult):
    data: Optional[List[MedicalPosition]]


@strawberry.type
class StaffTypeResult(RequestResult):
    data: Optional[List[StaffType]]


@strawberry.type
class DoctorCategoryResult(RequestResult):
    data: Optional[List[DoctorCategory]]


@strawberry.type
class DoctorStatusTypeResult(RequestResult):
    data: Optional[List[DoctorStatusType]]


@strawberry.type
class DoctorStatusResult(RequestResult):
    data: Optional[List[DoctorStatus]]


@strawberry.type
class PatientTypeResult(RequestResult):
    data: Optional[List[PatientType]]


@strawberry.type
class DoctorMedicalCenterResult(RequestResult):
    data: Optional[List[DoctorMedicalCenter]]


@strawberry.type
class DoctorPatientTypeResult(RequestResult):
    data: Optional[List[DoctorPatientType]]


@strawberry.type
class ServiceMedicalSpecialityResult(RequestResult):
    data: Optional[List[ServiceMedicalSpeciality]]


@strawberry.type
class ComplexServiceResult(RequestResult):
    data: Optional[List[ComplexService]]


@strawberry.type
class ComplexServiceItemResult(RequestResult):
    data: Optional[List[ComplexServiceItem]]


@strawberry.type
class FinancialTypeResult(RequestResult):
    data: Optional[List[FinancialType]]


@strawberry.type
class ShifrResult(RequestResult):
    data: Optional[List[Shifr]]


@strawberry.type
class PolicyResult(RequestResult):
    data: Optional[List[Policy]]


@strawberry.type
class UserSubscribeResult(RequestResult):
    data: Optional[List[UserSubscribe]]


@strawberry.type
class DoctorReplacementResult(RequestResult):
    data: Optional[List[DoctorReplacement]]


@strawberry.type
class SubscribeDoctorResult(RequestResult):
    data: Optional[List[SubscribeDoctor]]


@strawberry.type
class PackTypeResult(RequestResult):
    data: Optional[List[PackType]]


@strawberry.type
class SubscribeServicePackResult(RequestResult):
    data: Optional[List[SubscribeServicePack]]


@strawberry.type
class SubscribeSpackRecordResult(RequestResult):
    data: Optional[List[SubscribeSpackRecord]]


@strawberry.type
class ShifrDiscountPeriodResult(RequestResult):
    data: Optional[List[ShifrDiscountPeriod]]


@strawberry.type
class ShifrDiscountResult(RequestResult):
    data: Optional[List[ShifrDiscount]]


@strawberry.type
class UserPurchaseResult(RequestResult):
    data: Optional[List[UserPurchase]]


@strawberry.type
class PricePeriodResult(RequestResult):
    data: Optional[List[PricePeriod]]


@strawberry.type
class PriceNameResult(RequestResult):
    data: Optional[List[PriceName]]


@strawberry.type
class PaymentTypeResult(RequestResult):
    data: Optional[List[PaymentType]]


@strawberry.type
class UserPaymentResult(RequestResult):
    data: Optional[List[UserPayment]]


@strawberry.type
class UserPurchaseReturnResult(RequestResult):
    data: Optional[List[UserPurchaseReturn]]


@strawberry.type
class RefuseReasonResult(RequestResult):
    data: Optional[List[RefuseReason]]


@strawberry.type
class UserServicePlanResult(RequestResult):
    data: Optional[List[UserServicePlan]]


@strawberry.type
class MedicalSpecialityWithMcenterDoctors(MedicalSpeciality):
    doctor_mcenter_list: Optional[List[DoctorMedicalCenter]] = None


@strawberry.type
class MedicalPositionWithMcenterDoctors(MedicalPosition):
    doctor_mcenter_list: Optional[List[DoctorMedicalCenter]] = None


@strawberry.type
class ServiceWithPrice:
    medical_center: Optional[MedicalCenter]
    service: Optional[Service] = None
    price: Optional[Price] = None
    discount: Optional[float] = None
    discounted_price: Optional[float] = None
    available_in_user_suscribe: Optional[bool] = None


@strawberry.type
class ServiceGroupWithPrice(ServiceGroup):
    wservices: Optional[List[ServiceWithPrice]] = None
    xmembers: Optional[List["ServiceGroupWithPrice"]] = None


@strawberry.type
class AccessTicketResult(RequestResult):
    data: Optional[List[AccessTicket]]
    medical_speciality_list: Optional[List[MedicalSpecialityWithMcenterDoctors]] = None
    medical_position_list: Optional[List[MedicalPositionWithMcenterDoctors]] = None
    doctor_mcenter_list: Optional[List[DoctorMedicalCenter]] = None
    service_group_with_services_list: Optional[List[ServiceGroupWithPrice]] = None
    dates_list: Optional[List[str]] = None
    medical_centers_list: Optional[List[MedicalCenter]] = None
    services_plain_list: Optional[List[ServiceWithPrice]] = None


@strawberry.type
class DoctorMedicalCenterServiceResult(RequestResult):
    data: Optional[List[DoctorMedicalCenterService]]


@strawberry.type
class MedicalCenterPriceNameResult(RequestResult):
    data: Optional[List[MedicalCenterPriceName]]


@strawberry.type
class UserDefaultObjectResult(RequestResult):
    data: Optional[List[UserDefaultObject]]


@strawberry.input
class MedicalCenterInput(MedicalCenterIn):
    id: Optional[List[int]] = None
    city: Optional[CityIn] = None


@strawberry.input
class ServiceTypeInput(ServiceTypeIn):
    id: Optional[List[int]] = None


@strawberry.input
class CityInput(CityIn):
    id: Optional[list[int]] = None


@strawberry.input
class ServiceDirectionInput(ServiceDirectionIn):
    id: Optional[List[int]] = None


@strawberry.input
class ServiceGroupInput(ServiceGroupIn):
    id: Optional[List[int]] = None


@strawberry.input
class ServiceInput(ServiceIn):
    id: Optional[List[int]] = None
    minimal_age: Optional[IntFilteringInterval] = None
    maximal_age: Optional[IntFilteringInterval] = None
    service_group: Optional[ServiceGroupIn] = None


@strawberry.input
class MedicalSpecialityInput(MedicalSpecialityIn):
    id: Optional[List[int]] = None


@strawberry.input
class DoctorInput(DoctorIn):
    id: Optional[List[int]] = None
    doctor_category: Optional[DoctorCategoryIn] = None


@strawberry.input
class DoctorMspecialityInput(DoctorMspecialityIn):
    id: Optional[List[int]] = None


@strawberry.input
class DoctorServiceInput(DoctorServiceIn):
    id: Optional[List[int]] = None


@strawberry.input
class PriceInput(PriceIn):
    id: Optional[List[int]] = None
    service: Optional[ServiceIn] = None
    price_period: Optional[PricePeriodIn] = None
    price_name: Optional[PriceNameIn] = None
    price_beznal: Optional[IntFilteringInterval] = None
    price_nal: Optional[IntFilteringInterval] = None


@strawberry.input
class DoctorScheduleInput(DoctorScheduleIn):
    id: Optional[List[int]] = None
    plan_visit_time: Optional[DateTimeFilteringInterval] = None
    paln_visit_duration: Optional[IntFilteringInterval] = None


@strawberry.input
class MedicalPositionInput(MedicalPositionIn):
    id: Optional[List[int]] = None


@strawberry.input
class StaffTypeInput(StaffTypeIn):
    id: Optional[List[int]] = None


@strawberry.input
class DoctorCategoryInput(DoctorCategoryIn):
    id: Optional[List[int]] = None


@strawberry.input
class DoctorStatusTypeInput(DoctorStatusTypeIn):
    id: Optional[List[int]] = None


@strawberry.input
class DoctorStatusInput(DoctorStatusIn):
    id: Optional[List[int]] = None
    doctor: Optional[DoctorIn] = None
    status_type: Optional[DoctorStatusTypeIn] = None


@strawberry.input
class PatientTypeInput(PatientTypeIn):
    id: Optional[List[int]] = None


@strawberry.input
class DoctorMedicalCenterInput(DoctorMedicalCenterIn):
    id: Optional[List[int]] = None
    doctor: Optional[DoctorIn] = None
    medical_speciality: Optional[MedicalSpecialityIn] = None
    medical_center: Optional[MedicalCenterIn] = None
    medical_position: Optional[MedicalPositionIn] = None
    staff_type: Optional[StaffTypeIn] = None


@strawberry.input
class DoctorPatientTypeInput(DoctorPatientTypeIn):
    id: Optional[List[int]] = None
    doctor_medical_center: Optional[DoctorMedicalCenterIn] = None
    patient_type: Optional[PatientTypeIn] = None


@strawberry.input
class ServiceMedicalSpecialityInput(ServiceMedicalSpecialityIn):
    id: Optional[List[int]] = None
    service: Optional[ServiceIn] = None
    medical_speciality: Optional[MedicalSpecialityIn] = None


@strawberry.input
class ComplexServiceInput(ComplexServiceIn):
    id: Optional[List[int]] = None
    service: Optional[ServiceIn] = None


@strawberry.input
class ComplexServiceItemInput(ComplexServiceItemIn):
    id: Optional[List[int]] = None
    complex_service: Optional[ComplexServiceIn] = None
    service: Optional[ServiceIn] = None


@strawberry.input
class FinancialTypeInput(FinancialTypeIn):
    id: Optional[List[int]] = None


@strawberry.input
class ShifrInput(ShifrIn):
    id: Optional[List[int]] = None
    financial_type: Optional[FinancialTypeIn] = None


@strawberry.input
class PolicyInput(PolicyIn):
    id: Optional[List[int]] = None
    user: Optional[UserIn] = None
    shifr: Optional[ShifrIn] = None


@strawberry.input
class UserSubscribeInput(UserSubscribeIn):
    id: Optional[List[int]] = None
    policy: Optional[PolicyIn] = None
    service: Optional[ServiceIn] = None


@strawberry.input
class DoctorReplacementInput(DoctorReplacementIn):
    id: Optional[List[int]] = None
    doctor: Optional[DoctorIn] = None


@strawberry.input
class SubscribeDoctorInput(SubscribeDoctorIn):
    id: Optional[List[int]] = None
    user_subscribe: Optional[UserSubscribeIn] = None
    doctor: Optional[DoctorIn] = None
    doctor_replacement: Optional[DoctorReplacementIn] = None


@strawberry.input
class PackTypeInput(PackTypeIn):
    id: Optional[List[int]] = None


@strawberry.input
class SubscribeServicePackInput(SubscribeServicePackIn):
    id: Optional[List[int]] = None
    user_subscribe: Optional[UserSubscribeIn] = None
    pack_type: Optional[PackTypeIn] = None


@strawberry.input
class SubscribeSpackRecordInput(SubscribeSpackRecordIn):
    id: Optional[List[int]] = None
    subscribe_services_pack: Optional[SubscribeServicePackIn] = None
    service: Optional[ServiceIn] = None
    service_group: Optional[ServiceGroupIn] = None


@strawberry.input
class ShifrDiscountPeriodInput(ShifrDiscountPeriodIn):
    id: Optional[List[int]] = None


@strawberry.input
class ShifrDiscountInput(ShifrDiscountIn):
    id: Optional[List[int]] = None
    shift_discount_period: Optional[ShifrDiscountPeriodIn] = None
    service: Optional[ServiceIn] = None
    service_group: Optional[ServiceGroupIn] = None
    shifr: Optional[ShifrIn] = None


@strawberry.input
class UserPurchaseInput(UserPurchaseIn):
    id: Optional[List[int]] = None
    user: Optional[UserIn] = None
    policy: Optional[PolicyIn] = None
    shifr: Optional[ShifrIn] = None
    doctor_mcenter_exec: Optional[DoctorMedicalCenterIn] = None
    doctor_mcenter_nurse: Optional[DoctorMedicalCenterIn] = None
    service: Optional[ServiceIn] = None
    user_payment: Optional[UserPaymentIn] = None


@strawberry.input
class UserPurchaseInMut:
    service_id: Optional[List[int]] = None
    service_quantity: Optional[int] = None


@strawberry.input
class PricePeriodInput(PricePeriodIn):
    id: Optional[List[int]] = None


@strawberry.input
class PriceNameInput(PriceNameIn):
    id: Optional[List[int]] = None


@strawberry.input
class PaymentTypeInput(PaymentTypeIn):
    id: Optional[List[int]] = None


@strawberry.input
class UserPaymentInput(UserPaymentIn):
    id: Optional[List[int]] = None
    user: Optional[UserIn] = None
    policy: Optional[PolicyIn] = None
    shifr: Optional[ShifrIn] = None
    payment_type: Optional[PaymentTypeIn] = None
    linked_user_payment: Optional['UserPaymentInput'] = None


@strawberry.input
class UserPurchaseReturnInput(UserPurchaseReturnIn):
    id: Optional[List[int]] = None
    user_purchase: Optional[UserPurchaseIn] = None
    user_payments: Optional[UserPaymentIn] = None


@strawberry.input
class RefuseReasonInput(RefuseReasonIn):
    id: Optional[List[int]] = None


@strawberry.input
class UserServicePlanInput(UserServicePlanIn):
    id: Optional[List[int]] = None
    service: Optional[ServiceIn] = None
    user: Optional[UserIn] = None
    shifr: Optional[ShifrIn] = None
    policy: Optional[PolicyIn] = None
    doctor_send: Optional[DoctorMedicalCenterIn] = None
    medical_center: Optional[MedicalCenterIn] = None
    refuse_reason: Optional[RefuseReasonIn] = None
    user_service_cart: Optional[UserServiceCartIn] = None


@strawberry.input
class AccessTicketInput(AccessTicketIn):
    id: Optional[List[int]] = None
    doctor_mcenters: Optional[DoctorMedicalCenterIn] = None
    user: Optional[UserIn] = None
    ticket_datetime: Optional[DateTimeFilteringInterval]


@strawberry.input
class AccessTicketInputSort(AccessTicketIn):
    id: Optional[List[int]] = None
    doctor_mcenters: Optional[DoctorMedicalCenterIn] = None
    user: Optional[UserIn] = None


@strawberry.input
class DoctorMedicalCenterServiceInput(DoctorMedicalCenterServiceIn):
    id: Optional[List[int]] = None
    service: Optional[ServiceIn] = None
    doctor_mcenters: Optional[DoctorMedicalCenterIn] = None


@strawberry.input
class MedicalCenterPriceNameInput(MedicalCenterPriceNameIn):
    id: Optional[List[int]] = None
    medical_center: Optional[MedicalCenterIn] = None
    price_name: Optional[PriceNameIn] = None
    service_type: Optional[ServiceTypeIn] = None


@strawberry.input
class UserDefaultObjectInput(UserDefaultObjectIn):
    id: Optional[List[int]] = None
    default_patient: Optional[UserIn] = None
    default_medical_center: Optional[MedicalCenterIn] = None
    default_doctor_mcenters: Optional[DoctorMedicalCenterIn] = None


@strawberry.type
class SubscribeCommonInfo:
    medical_center: Optional[MedicalCenter] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    service_manager: Optional[DoctorMedicalCenter] =None
    trusted_pediatrician: Optional[DoctorMedicalCenter] = None
    specialists: Optional[List[SubscribeDoctor]] = None


@strawberry.type
class SubscribeServiceGroupWithServices:
    service_group: Optional[ServiceGroup] = None
    services: Optional[List[SubscribeSpackRecord]] = None


@strawberry.type
class SubscribeServicePackWithQuantity:
    service_pack: Optional[SubscribeServicePack] = None
    services_quantity: Optional[int] = None


@strawberry.type
class PolicyPaymentPlanWithDebt:
    id: Optional[int] = None
    client_id: Optional[str] = None
    policy_id: Optional[int] = None
    planed_date: Optional[datetime] = None
    amount: Optional[float] = None
    debt: Optional[float] = None
    show_payment_button: Optional[bool] = None


@strawberry.type
class SubscribeFinance:
    subscribe_price: Optional[float] = None
    subscribe_discount: Optional[float] = None
    subscribe_payment_plan: Optional[List[PolicyPaymentPlanWithDebt]] = None
    common_subscribe_debt: Optional[float] = None


@strawberry.type
class SubscribeInfoBlocks:
    common_block: Optional[SubscribeCommonInfo] = None
    description_block: Optional[str] = None
    services_block: Optional[List[SubscribeServicePackWithQuantity]] = None
    financial_block: Optional[SubscribeFinance] = None


@strawberry.type
class SubscribeInfoBlocksResult(RequestResult):
    data: Optional[SubscribeInfoBlocks]


@strawberry.input
class PolicyPaymentPlanInput(PolicyPaymentPlanIn):
    id: Optional[List[int]] = None


@strawberry.input
class PayKeeperPaymentDataInput(PayKeeperPaymentDataIn):
    id: Optional[List[int]] = None
    user_payment: Optional[UserPaymentIn]


@strawberry.type
class EventsCalendar:
    user_id: Optional[int] = None
    user_fio: Optional[str] = None
    user_birth_date: Optional[date] = None 
    doctors_fio: Optional[str] = None
    doctors_position: Optional[str] = None
    service_date_and_time: Optional[datetime] = None
    service_name: Optional[str] = None
    service_preparation_rules: Optional[str] = None
    service_duration: Optional[str] = None
    medical_center_name: Optional[str] = None
    medical_center_address: Optional[str] = None
    room_number: Optional[str] = None
    is_paid: Optional[bool] = None
    is_done: Optional[bool] = None
    is_canceled: Optional[bool] = None
    user_service_cart_client_id: Optional[str] = None
    access_ticket_client_id: Optional[str] = None
    payment_id: Optional[int] = None
    doctor_mcenters_id: Optional[int] = None
    service_id: Optional[int] = None
    medical_center_id: Optional[int] = None
    payment_method: Optional[str] = None


@strawberry.type
class EventsCalendarResult(RequestResult):
    data: Optional[List[EventsCalendar]] = None


@strawberry.type
class VisitHistoryRecord:
    user_services_carts_client_id: Optional[str] = None
    user_services_plans_client_id: Optional[str] = None
    service_name: Optional[str] = None
    service_data: Optional[datetime] = None
    service_doctor: Optional[DoctorMedicalCenter] = None
    service_status: Optional[str] = None
    obtaining_method: Optional[str] = None
    user: Optional[User] = None


@strawberry.type
class VisitHistoryRecordResult(RequestResult):
    data: Optional[List[VisitHistoryRecord]] = None
