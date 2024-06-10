import strawberry
from datetime import datetime, date, time

from typing import Optional, List


@strawberry.input
class BaseIn:
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class IntFilteringInterval:
    equals: Optional[int] = None
    less: Optional[int] = None
    more: Optional[int] = None
    less_or_equals: Optional[int] = None
    more_or_equals: Optional[int] = None


@strawberry.input
class DateTimeFilteringInterval:
    equals: Optional[datetime] = None
    less: Optional[datetime] = None
    more: Optional[datetime] = None
    less_or_equals: Optional[datetime] = None
    more_or_equals: Optional[datetime] = None


@strawberry.type
class RequestResult:
    data: Optional[str] = None
    records_count: Optional[int] = None
    pages_count: Optional[int] = None
    status_code: Optional[int] = None
    details: Optional[str] = None
    details_ru: Optional[str] = None


@strawberry.type
class OracleProcResult(RequestResult):
    data: Optional[List[str]] = None


@strawberry.input
class MedicalCenterIn:

    client_id: Optional[List[int]] = None
    city_id: Optional[List[int]] = None
    name: Optional[str] = None
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    description: Optional[str] = None
    inn: Optional[str] = None
    bank_bic: Optional[str] = None
    settlement_account: Optional[str] = None
    correspondent_account: Optional[str] = None
    kpp:Optional[str] = None
    is_active: Optional[bool] = None
    logo: Optional[str] = None
    website_url: Optional[str] = None
    phone_fax: Optional[str] = None
    dms_phone: Optional[str] = None
    collection_tests_time: Optional[str] = None
    work_time: Optional[str] = None
    collection_tests_time:Optional[str] = None
    vaccination_time: Optional[str] = None
    lpu_id: Optional[List[int]] = None
    show_in_lk: Optional[bool] = None


@strawberry.input
class ServiceTypeIn:

    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class CityIn:

    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class ServiceDirectionIn:

    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class ServiceGroupIn:

    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    view_name: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None
    client_service_group_code: Optional[str] = None
    level_sorting_code: Optional[int] = None
    is_active: Optional[bool] = None


@strawberry.input
class ServiceIn:

    client_id: Optional[List[int]] = None
    service_type_id: Optional[List[int]] = None
    service_group_id: Optional[List[int]] = None
    name_for_staff: Optional[str] = None
    name_for_mz: Optional[str] = None
    name_for_lk: Optional[str] = None
    full_description: Optional[str] = None
    applied_method: Optional[str] = None
    preparation_rules: Optional[str] = None
    short_description: Optional[str] = None
    comment: Optional[str] = None
    mz_code: Optional[str] = None
    execution_time: Optional[int] = None
    nurses_execution_time: Optional[int] = None
    minimal_age: Optional[int] = None
    maximal_age: Optional[int] = None
    gender: Optional[str] = None
    is_urgent: Optional[bool] = None
    is_for_home_only: Optional[bool] = None
    selected_service_notification: Optional[str] = None
    is_complex_service: Optional[bool] = None
    client_service_code: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class MedicalSpecialityIn:

    client_id: Optional[List[int]] = None
    view_name: Optional[str] = None
    search_name: Optional[str] = None
    view_description: Optional[str] = None
    search_description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class DoctorCategoryIn:

    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

@strawberry.input
class DoctorIn:

    client_id: Optional[List[int]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    birth_date: Optional[date] = None
    photo: Optional[str] = None
    doctor_category_id: Optional[List[int]] = None
    private_phone: Optional[str] = None
    work_phone: Optional[str] = None
    email: Optional[str] = None
    common_experience: Optional[int] = None
    is_active: Optional[bool] = None


@strawberry.input
class DoctorMspecialityIn:

    doctor_id: Optional[List[int]] = None
    mspeciality_id: Optional[List[int]] = None
    is_active: Optional[bool] = None


@strawberry.input
class DoctorServiceIn:

    doctor_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    is_active: Optional[bool] = None
    doctor: Optional[DoctorIn] = None
    service: Optional[ServiceIn] = None


@strawberry.input
class PriceIn:

    client_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    price_period_id: Optional[List[int]] = None
    price_name_id: Optional[List[int]] = None
    price_beznal: Optional[float] = None
    price_nal: Optional[float] = None


@strawberry.input
class DoctorScheduleIn:

    doctor_id: Optional[List[int]] = None
    plan_visit_time: Optional[datetime] = None
    paln_visit_duration: Optional[int] = None
    description: Optional[str] = None
    is_available: Optional[bool] = None


@strawberry.input
class MedicalPositionIn:

    client_id: Optional[List[int]] = None
    view_name: Optional[str] = None
    search_name: Optional[str] = None
    view_description: Optional[str] = None
    search_description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class StaffTypeIn:

    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class DoctorStatusTypeIn:

    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class DoctorStatusIn:

    doctor_id: Optional[List[int]] = None
    status_type_id: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@strawberry.input
class PatientTypeIn(BaseIn):

    client_id: Optional[List[int]] = None


@strawberry.input
class DoctorMedicalCenterIn:

    id: Optional[List[int]] = None
    client_id: Optional[List[int]] = None
    doctor_id: Optional[List[int]] = None
    medical_speciality_id: Optional[List[int]] = None
    medical_center_id: Optional[List[int]] = None
    medical_position_id: Optional[List[int]] = None
    staff_type_id: Optional[List[int]] = None
    show_in_lk: Optional[bool] = None
    minimal_age: Optional[IntFilteringInterval] = None
    maximal_age: Optional[IntFilteringInterval] = None
    is_active: Optional[bool] = None
    doctor: Optional[DoctorIn] = None
    medical_center: Optional[MedicalCenterIn] = None


@strawberry.input
class DoctorPatientTypeIn:

    client_id: Optional[List[int]] = None
    doctor_medical_center_id: Optional[List[int]] = None
    patient_type_id: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


@strawberry.input
class ServiceMedicalSpecialityIn:
    service_id: Optional[List[int]] = None
    medical_speciality_id: Optional[List[int]] = None
    is_active: Optional[bool] = None


@strawberry.input
class ComplexServiceIn:
    service_id: Optional[List[int]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class ComplexServiceItemIn:
    complex_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    comment: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    coefficient_to_price: Optional[float] = None
    is_active: Optional[bool] = None


@strawberry.input
class FinancialTypeIn(BaseIn):

    client_id: Optional[List[int]] = None


@strawberry.input
class ShifrIn:
    client_id: Optional[List[int]] = None
    code: Optional[str] = None
    name: Optional[str] = None
    company_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[int] = None
    financial_type_id: Optional[List[int]] = None
    is_active: Optional[bool] = None


@strawberry.input
class PolicyIn:
    id: Optional[int] = None
    client_id: Optional[List[int]] = None
    user_id: Optional[List[int]] = None
    shifr_id: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[int] = None
    series: Optional[str] = None
    number: Optional[str] = None
    contract_date: Optional[date] = None
    price: Optional[float] = None
    discount: Optional[float] = None
    discount_coefficien: Optional[float] = None
    amount: Optional[float] = None
    current_paid: Optional[float] = None
    is_active: Optional[bool] = None


@strawberry.input
class UserIn:
    id: Optional[int] = None
    client_id: Optional[List[int]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    additional_phone_number: Optional[str] = None
    doc_type: Optional[int] = None
    doc_series: Optional[str] = None
    doc_number: Optional[str] = None
    doc_giving_dep_name: Optional[str] = None
    doc_giving_dep_code: Optional[str] = None
    doc_date: Optional[date] = None
    doc_reg_address: Optional[str] = None
    snils: Optional[str] = None
    inn: Optional[str] = None
    city_id: Optional[List[int]] = None
    address_full: Optional[str] = None
    address_mis_kladr_id: Optional[List[int]] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    zone_number: Optional[int] = None
    default_medical_center_id: Optional[List[int]] = None
    login_phone_number: Optional[str] = None
    password: Optional[str] = None
    is_verified: Optional[bool] = None
    info_way_id: Optional[List[int]] = None
    notification_time: Optional[time] = None
    pref_notification_contact_id: Optional[List[int]] = None
    is_active: Optional[bool] = None
    created: Optional[date] = None


@strawberry.input
class UserSubscribeIn(BaseIn):
    id: Optional[int] = None
    client_id: Optional[List[int]] = None
    policy_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    policy: Optional[PolicyIn] = None
    service: Optional[ServiceIn] = None


@strawberry.input
class DoctorReplacementIn:
    client_id: Optional[List[int]] = None
    doctor_id: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class SubscribeDoctorIn:
    client_id: Optional[List[int]] = None
    user_subscribe_id: Optional[List[int]] = None
    doctor_id: Optional[List[int]] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    role_id: Optional[List[int]] = None
    doctor_replacement_id: Optional[List[int]] = None
    is_active: Optional[bool] = None


@strawberry.input
class PackTypeIn(BaseIn):
    client_id: Optional[List[int]] = None


@strawberry.input
class SubscribeServicePackIn:
    client_id: Optional[List[int]] = None
    user_subscribe_id: Optional[List[int]] = None
    code: Optional[str] = None
    pack_type_id: Optional[List[int]] = None
    pack_tag: Optional[int] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None
    user_subscribe: Optional[UserSubscribeIn] = None
    pack_type: Optional[PackTypeIn] = None


@strawberry.input
class SubscribeSpackRecordIn:
    client_id: Optional[List[int]] = None
    subscribe_services_pack_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    service_group_id: Optional[List[int]] = None
    quantity: Optional[int] = None
    is_active: Optional[bool] = None
    subscribe_services_pack: Optional[SubscribeServicePackIn] = None
    service: Optional[ServiceIn] = None
    service_group: Optional[ServiceGroupIn] = None


@strawberry.input
class ShifrDiscountPeriodIn:
    client_id: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@strawberry.input
class ShifrDiscountIn:
    client_id: Optional[List[int]] = None
    shift_discount_period_id: Optional[List[int]] = None
    service_group_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    shifr_id: Optional[List[int]] = None
    comment: Optional[str] = None
    discount_coefficient_a: Optional[float] = None
    discount_coefficient_s: Optional[float] = None


@strawberry.input
class UserPurchaseIn:
    client_id: Optional[List[int]] = None
    user_id: Optional[List[int]] = None
    policy_id: Optional[List[int]] = None
    shifr_id: Optional[List[int]] = None
    user_payment_id: Optional[List[int]] = None
    doctor_exec_id: Optional[List[int]] = None
    doctor_nurse_id: Optional[List[int]] = None
    payment_date: Optional[datetime] = None
    service_id: Optional[List[int]] = None
    service_quantity: Optional[int] = None
    price: Optional[float] = None
    discount: Optional[float] = None
    discount_koef: Optional[float] = None
    amount: Optional[float] = None
    # user: Optional[UserIn] = None
    # policy: Optional[PolicyIn] = None
    # shifr: Optional[ShifrIn] = None
    # doctor_mcenter_exec: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_nurse: Optional[DoctorMedicalCenterIn] = None
    service: Optional[ServiceIn] = None
    user_payment: Optional['UserPaymentIn'] = None


@strawberry.input
class PricePeriodIn:
    client_id: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


@strawberry.input
class PriceNameIn:
    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class PaymentTypeIn:
    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class LpuIn:
    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None

@strawberry.input
class UserPaymentIn:
    id: Optional[int] = None
    client_id: Optional[List[int]] = None
    user_id: Optional[List[int]] = None
    policy_id: Optional[List[int]] = None
    shifr_id: Optional[List[int]] = None
    payment_type_id: Optional[List[int]] = None
    linked_user_payment_id: Optional[List[int]] = None
    avance_status: Optional[int] = None
    payment_date: Optional[date] = None
    payment_status: Optional[int] = None
    amount: Optional[float] = None
    full_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    used_amount: Optional[float] = None
    avance_amount: Optional[float] = None
    card_amount: Optional[float] = None
    sbp_amount: Optional[float] = None
    debt_amount: Optional[float] = None
    edit_now_status: Optional[bool] = None
    lpu_id: Optional[List[int]] = None
    cashier_id: Optional[List[int]] = None
    transaction_code: Optional[str] = None
    # user: Optional[UserIn] = None
    # policy: Optional[PolicyIn] = None
    # shifr: Optional[ShifrIn] = None
    payment_type: Optional[PaymentTypeIn] = None
    # linked_user_payment: Optional['UserPaymentIn'] = None
    lpu: Optional[LpuIn] = None


@strawberry.input
class UserPurchaseReturnIn:
    client_id: Optional[List[int]] = None
    user_purchase_id: Optional[List[int]] = None
    user_payments_id: Optional[List[int]] = None
    quantity: Optional[int] = None
    sum: Optional[float] = None
    sum_card: Optional[float] = None
    sum_sbp: Optional[float] = None
    sum_avance: Optional[float] = None


@strawberry.input
class RefuseReasonIn:
    client_id: Optional[List[int]] = None
    text: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class AccessTicketIn:
    client_id: Optional[List[int]] = None
    doctor_mcenters_id: Optional[List[int]] = None
    user_id: Optional[List[int]] = None
    ticket_datetime: Optional[datetime] = None
    ticket_duration: Optional[int] = None
    ticket_room: Optional[str] = None
    status: Optional[bool] = None
    firststatus: Optional[bool] = None
    bl_status: Optional[int] = None
    is_active: Optional[bool] = None
    is_reserv: Optional[bool] = None
    expire_date: Optional[datetime] = None
    from_internet_status: Optional[bool] = None


@strawberry.input
class UserServiceCartIn:
    client_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    user_id: Optional[List[int]] = None
    shifr_id: Optional[List[int]] = None
    policy_id: Optional[List[int]] = None
    medical_center_id: Optional[List[int]] = None
    access_ticket_id: Optional[List[int]] = None
    doctor_mcenter_id: Optional[List[int]] = None
    doctor_mcenter_exec_id: Optional[List[int]] = None
    doctor_mcenter_send_id: Optional[List[int]] = None
    doctor_mcenter_nurse_id: Optional[List[int]] = None
    doctor_mcenter_paramedic_id: Optional[List[int]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    complex_service_id: Optional[List[int]] = None
    complex_service_status: Optional[int] = None
    service_status: Optional[int] = None
    quantity: Optional[int] = None
    stac_satus: Optional[bool] = None
    cito_status: Optional[bool] = None
    refuse_date: Optional[date] = None
    refuse_reason_id: Optional[List[int]] = None
    description: Optional[str] = None
    discount: Optional[float] = None
    discount_coefficient: Optional[float] = None
    price_id: Optional[List[int]] = None
    user_purchase_id: Optional[List[int]] = None
    service: Optional[ServiceIn] = None
    user: Optional[UserIn] = None
    shifr: Optional[ShifrIn] = None
    policy: Optional[PolicyIn] = None
    medical_center: Optional[MedicalCenterIn] = None
    access_ticket: Optional[AccessTicketIn] = None
    # doctor_mcenter: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_exec: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_send: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_nurse: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_paramedic: Optional[DoctorMedicalCenterIn] = None
    complex_service: Optional[ComplexServiceIn] = None
    user_purchase: Optional[UserPurchaseIn] = None
    refuse_reason: Optional[RefuseReasonIn] = None
    price: Optional[PriceIn] = None


@strawberry.type
class UserServiceCartOut:
    client_id: Optional[int] = None
    service_id: Optional[int] = None
    user_id: Optional[int] = None
    shifr_id: Optional[int] = None
    policy_id: Optional[int] = None
    medical_center_id: Optional[int] = None
    access_ticket_id: Optional[int] = None
    doctor_mcenter_id: Optional[int] = None
    doctor_mcenter_exec_id: Optional[int] = None
    doctor_mcenter_send_id: Optional[int] = None
    doctor_mcenter_nurse_id: Optional[int] = None
    doctor_mcenter_paramedic_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    complex_service_id: Optional[int] = None
    complex_service_status: Optional[int] = None
    service_status: Optional[int] = None
    quantity: Optional[int] = None
    stac_satus: Optional[bool] = None
    cito_status: Optional[bool] = None
    refuse_date: Optional[date] = None
    refuse_reason_id: Optional[int] = None
    description: Optional[str] = None
    discount: Optional[float] = None
    discount_coefficient: Optional[float] = None
    price_id: Optional[int] = None
    user_purchase_id: Optional[int] = None


@strawberry.input
class UserServicePlanIn:
    client_id: Optional[List[int]] = None
    user_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    policy_id: Optional[List[int]] = None
    shifr_id: Optional[List[int]] = None
    quantity: Optional[int] = None
    plan_date: Optional[date] = None
    description: Optional[str] = None
    doctor_send_id: Optional[List[int]] = None
    medical_center_id: Optional[List[int]] = None
    status: Optional[int] = None
    refuse_reason_id: Optional[List[int]] = None
    refuse_date: Optional[date] = None
    user_service_cart_id: Optional[List[int]] = None


@strawberry.input
class UserAdminIn:
    client_id: Optional[List[int]] = None
    user_id: Optional[List[int]] = None
    registration_visible_fields: Optional[str] = None
    registration_required_fields: Optional[str] = None


@strawberry.input
class UserRelativeIn:
    user_id: Optional[List[int]] = None
    relative_id: Optional[List[int]] = None
    relationship_degree_id: Optional[List[int]] = None
    extra_rights: Optional[bool] = None
    block_status: Optional[bool] = None


@strawberry.input
class RelationshipDegreesIn:
    client_id: Optional[List[int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.input
class DoctorMedicalCenterServiceIn:
    client_id: Optional[List[int]] = None
    service_id: Optional[List[int]] = None
    doctor_mcenters_id: Optional[List[int]] = None
    is_active: Optional[bool] = None


@strawberry.input
class MedicalCenterPriceNameIn:
    client_id: Optional[List[int]] = None
    medical_center_id: Optional[List[int]] = None
    price_name_id: Optional[List[int]] = None
    service_type_id: Optional[List[int]] = None
    is_active: Optional[bool] = None


@strawberry.input
class UserDefaultObjectIn:
    user_id: Optional[int] = None
    default_patient_id: Optional[int] = None
    default_medical_center_id: Optional[int] = None
    default_doctor_mcenters_id: Optional[int] = None


@strawberry.input
class PolicyPaymentPlanIn:
    client_id: Optional[List[int]] = None
    policy_id: Optional[List[int]] = None
    planed_date: Optional[str] = None
    amount: Optional[float] = None


@strawberry.input
class PayKeeperPaymentDataIn:
    user_payment_id: Optional[List[int]] = None
    paykeeper_id: Optional[List[int]] = None
    pay_amount: Optional[float] = None
    refund_amount: Optional[float] = None
    clientid: Optional[str] = None
    orderid: Optional[str] = None
    payment_system_id: Optional[str] = None
    unique_id: Optional[str] = None
    status: Optional[str] = None
    repeat_counter: Optional[int] = None
    pending_datetime: Optional[datetime] = None
    obtain_datetime: Optional[datetime] = None
    success_datetime: Optional[datetime] = None
    user_payment: Optional[UserPaymentIn] = None


@strawberry.type
class SubscribeNetNode:
    user_subscribe_id: Optional[int] = None
    pack_id: Optional[int] = None
    pack_type_id: Optional[int] = None
    pack_min_quantity: Optional[int] = None
    pack_max_quantity: Optional[int] = None
    pack_quantity: Optional[int] = None
    pack_record_service_id: Optional[int] = None
    pack_record_quantity: Optional[int] = None


@strawberry.type
class UserServiceCartSubscribe:
    service_id: int = None
    medical_center_id: int = None
    access_ticket_id: int = None
    doctor_mcenter_id: int = None
    quantity: Optional[int] = 1
    price_id: Optional[int] = None
    subscribe_id: Optional[int] = None
    error_message: Optional[str] = ''
    error_message_ru: Optional[str] = ''


@strawberry.type
class UserServiceCartSubscribeResult(RequestResult):
    data: Optional[UserServiceCartSubscribe]
