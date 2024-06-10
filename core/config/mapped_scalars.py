import strawberry
# import datetime
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper
from typing import Optional, List
# from pytz import timezone

from ..sa_tables.main_process import (StaffTypeTable,
                                      ServiceTypeTable, ServiceTable, MedicalSpecialityTable,
                                      DoctorTable, DoctorMspecialityTable, DoctorCategoryTable,
                                      ServiceGroupTable, MedicalPositionTable, DoctorStatusTypeTable,
                                      DoctorStatusTable, PatientTypeTable, DoctorMedicalCenterTable,
                                      DoctorPatientTypeTable, ServiceMedicalSpecialityTable, ComplexServiceTable,
                                      ComplexServiceItemTable, FinancialTypeTable, ShifrTable, PolicyTable,
                                      UserSubscribeTable, DoctorReplacementTable, SubscribeDoctorTable,
                                      PackTypeTable, SubscribeServicePackTable, SubscribeSpackRecordTable,
                                      ShifrDiscountPeriodTable, ShifrDiscountTable, UserPurchaseTable,
                                      PricePeriodTable, PriceNameTable, PriceTable, PaymentTypeTable, UserPaymentTable,
                                      UserPurchaseReturnTable, RefuseReasonTable, AccessTicketTable,
                                      UserServiceCartTable, UserServicePlanTable, DoctorMedicalCenterServiceTable,
                                      MedicalCenterPriceNameTable, UserDefaultObjectTable, PolicyPaymentPlanTable,
                                      PayKeeperPaymentDataTable, SubscribeRoleTable, UserDocumentRequestTable)
from ..sa_tables.accounts import (UserTable, MedicalCenterTable, CityTable, InformationWayTable,
                                  RelationshipDegreesTable, UserRelativeTable, LpuTable)
from ..sa_tables.admin import UserAdminTable


strawberry_sqlalchemy_mapper = StrawberrySQLAlchemyMapper()


@strawberry_sqlalchemy_mapper.type(CityTable)
class City:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(LpuTable)
class Lpu:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(MedicalCenterTable)
class MedicalCenter:
    client_id: Optional[str] = None
    city: Optional[City] = None
    lpu: Optional[Lpu] = None


@strawberry_sqlalchemy_mapper.type(StaffTypeTable)
class StaffType:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(DoctorCategoryTable)
class DoctorCategory:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(DoctorStatusTypeTable)
class DoctorStatusType:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(PatientTypeTable)
class PatientType:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(ServiceTypeTable)
class ServiceType:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(InformationWayTable)
class InformationWay:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(UserTable)
class User:
    __exclude__ = ["password"]
    client_id: Optional[str] = None
    city: Optional[City]
    default_medical_center: Optional[MedicalCenter]
    info_way: Optional[InformationWay]
    pref_notification_contact: Optional['User']


@strawberry_sqlalchemy_mapper.type(UserTable)
class UserShortened:
    __exclude__ = ["city", "default_medical_center", "info_way", "pref_notification_contact"]
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(ServiceTable)
class Service:
    client_id: Optional[str] = None
    service_type: Optional[ServiceType]
    service_group: Optional['ServiceGroup']


@strawberry_sqlalchemy_mapper.type(MedicalSpecialityTable)
class MedicalSpeciality:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(DoctorTable)
class Doctor:
    client_id: Optional[str] = None
    doctor_category: Optional[DoctorCategory] = None


@strawberry_sqlalchemy_mapper.type(DoctorStatusTable)
class DoctorStatus:
    doctor: Doctor
    status_type: DoctorStatusType


@strawberry_sqlalchemy_mapper.type(DoctorMspecialityTable)
class DoctorMspeciality:
    doctor: Optional[Doctor]
    mspeciality: Optional[MedicalSpeciality]


@strawberry_sqlalchemy_mapper.type(ServiceGroupTable)
class ServiceGroup:
    client_id: Optional[str] = None
    xmembers: Optional[List["ServiceGroup"]] = None
    path: Optional[List[str]] = None
    wservices: Optional[List[Service]] = None


@strawberry_sqlalchemy_mapper.type(MedicalPositionTable)
class MedicalPosition:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(DoctorMedicalCenterTable)
class DoctorMedicalCenter:
    client_id: Optional[str] = None
    doctor: Optional[Doctor]
    medical_speciality: Optional[MedicalSpeciality]
    medical_center: Optional[MedicalCenter]
    medical_position: Optional[MedicalPosition]
    staff_type: Optional[StaffType]


@strawberry_sqlalchemy_mapper.type(DoctorPatientTypeTable)
class DoctorPatientType:
    client_id: Optional[str] = None
    doctor_medical_center: Optional[DoctorMedicalCenter]
    patient_type: Optional[PatientType]


@strawberry_sqlalchemy_mapper.type(ServiceMedicalSpecialityTable)
class ServiceMedicalSpeciality:
    client_id: Optional[str] = None
    service: Optional[Service]
    medical_speciality: Optional[MedicalSpeciality]


@strawberry_sqlalchemy_mapper.type(ComplexServiceTable)
class ComplexService:
    client_id: Optional[str] = None
    service: Optional[Service]


@strawberry_sqlalchemy_mapper.type(ComplexServiceItemTable)
class ComplexServiceItem:
    complex_service: Optional[ComplexService]
    service: Optional[Service]


@strawberry_sqlalchemy_mapper.type(FinancialTypeTable)
class FinancialType:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(ShifrTable)
class Shifr:
    client_id: Optional[str] = None
    financial_type: Optional[FinancialType]


@strawberry_sqlalchemy_mapper.type(PolicyTable)
class Policy:
    client_id: Optional[str] = None
    user: Optional[User]
    shifr: Optional[Shifr]
    medical_center: Optional[MedicalCenter]


@strawberry_sqlalchemy_mapper.type(UserSubscribeTable)
class UserSubscribe:
    client_id: Optional[str] = None
    policy: Optional[Policy]
    service: Optional[Service]


@strawberry_sqlalchemy_mapper.type(DoctorReplacementTable)
class DoctorReplacement:
    client_id: Optional[str] = None
    doctor: Optional[Doctor]


@strawberry_sqlalchemy_mapper.type(SubscribeRoleTable)
class SubscribeRole:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(SubscribeDoctorTable)
class SubscribeDoctor:
    client_id: Optional[str] = None
    user_subscribe: Optional[UserSubscribe] = None
    doctor_mcenters: Optional[DoctorMedicalCenter] = None
    doctor_replacement: Optional[DoctorReplacement] = None
    role: Optional[SubscribeRole] = None


@strawberry_sqlalchemy_mapper.type(PackTypeTable)
class PackType:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(SubscribeServicePackTable)
class SubscribeServicePack:
    client_id: Optional[str] = None
    user_subscribe: Optional[UserSubscribe]
    pack_type: Optional[PackType]


@strawberry_sqlalchemy_mapper.type(SubscribeSpackRecordTable)
class SubscribeSpackRecord:
    client_id: Optional[str] = None
    subscribe_services_pack: Optional[SubscribeServicePack]
    service: Optional[Service]
    service_group: Optional[ServiceGroup]


@strawberry_sqlalchemy_mapper.type(ShifrDiscountPeriodTable)
class ShifrDiscountPeriod:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(ShifrDiscountTable)
class ShifrDiscount:
    client_id: Optional[str] = None
    shift_discount_period: Optional[ShifrDiscountPeriod]
    service: Optional[Service]
    service_group: Optional[ServiceGroup]
    shifr: Optional[Shifr]


@strawberry_sqlalchemy_mapper.type(UserPurchaseTable)
class UserPurchase:
    client_id: Optional[str] = None
    user: Optional[User]
    policy: Optional[Policy]
    shifr: Optional[Shifr]
    doctor_mcenter_exec: Optional[DoctorMedicalCenter]
    doctor_mcenter_nurse: Optional[DoctorMedicalCenter]
    service: Optional[Service]
    user_payment: Optional['UserPayment']


@strawberry_sqlalchemy_mapper.type(PricePeriodTable)
class PricePeriod:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(PriceNameTable)
class PriceName:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(PriceTable)
class Price:
    client_id: Optional[str] = None
    service: Optional[Service]
    price_period: Optional[PricePeriod]
    price_name: Optional[PriceName]


@strawberry_sqlalchemy_mapper.type(PaymentTypeTable)
class PaymentType:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(UserPaymentTable)
class UserPayment:
    client_id: Optional[str] = None
    user: Optional[User]
    policy: Optional[Policy]
    shifr: Optional[Shifr]
    payment_type: Optional[PaymentType]
    linked_user_payment: Optional['UserPayment']
    lpu: Optional[Lpu] = None


@strawberry_sqlalchemy_mapper.type(UserPurchaseReturnTable)
class UserPurchaseReturn:
    client_id: Optional[str] = None
    user_purchase: Optional[UserPurchase]
    user_payments: Optional[UserPayment]


@strawberry_sqlalchemy_mapper.type(RefuseReasonTable)
class RefuseReason:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(AccessTicketTable)
class AccessTicket:
    client_id: Optional[str] = None
    doctor_mcenters: Optional[DoctorMedicalCenter]
    user: Optional[User]


@strawberry_sqlalchemy_mapper.type(UserServiceCartTable)
class UserServiceCart:
    client_id: Optional[str] = None
    service: Optional[Service]
    user:Optional[User]
    shifr: Optional[Shifr]
    policy: Optional[Policy]
    medical_center: Optional[MedicalCenter]
    access_ticket: Optional[AccessTicket]
    doctor_mcenter: Optional[DoctorMedicalCenter]
    # doctor_mcenter_exec: Optional[DoctorMedicalCenter]
    # doctor_mcenter_send: Optional[DoctorMedicalCenter]
    # doctor_mcenter_nurse: Optional[DoctorMedicalCenter]
    # doctor_mcenter_paramedic: Optional[DoctorMedicalCenter]
    complex_service: Optional[ComplexService]
    user_purchase: Optional[UserPurchase]
    refuse_reason: Optional[RefuseReason]
    price: Optional[Price]


@strawberry_sqlalchemy_mapper.type(UserServicePlanTable)
class UserServicePlan:
    client_id: Optional[str] = None
    service: Optional[Service]
    user: Optional[User]
    shifr: Optional[Shifr]
    policy: Optional[Policy]
    doctor_send: Optional[DoctorMedicalCenter]
    medical_center: Optional[MedicalCenter]
    refuse_reason: Optional[RefuseReason]
    # user_service_cart: Optional[UserServiceCart]


@strawberry_sqlalchemy_mapper.type(UserAdminTable)
class UserAdmin:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(RelationshipDegreesTable)
class RelationshipDegrees:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(UserRelativeTable)
class UserRelative:
    client_id: Optional[str] = None
    user: Optional[User]
    relative: Optional[User]
    relationship_degree: Optional[RelationshipDegrees]


@strawberry_sqlalchemy_mapper.type(DoctorMedicalCenterServiceTable)
class DoctorMedicalCenterService:
    client_id: Optional[str] = None
    service: Optional[Service]
    doctor_mcenters: Optional[DoctorMedicalCenter]


@strawberry_sqlalchemy_mapper.type(MedicalCenterPriceNameTable)
class MedicalCenterPriceName:
    client_id: Optional[str] = None
    medical_center: Optional[MedicalCenter]
    price_name: Optional[PriceName]
    service_type: Optional[ServiceType]


@strawberry_sqlalchemy_mapper.type(UserDefaultObjectTable)
class UserDefaultObject:
    user: Optional[User]
    default_patient: Optional[User]
    default_medical_center: Optional[MedicalCenter]
    default_doctor_mcenters: Optional[DoctorMedicalCenter]


@strawberry_sqlalchemy_mapper.type(PolicyPaymentPlanTable)
class PolicyPaymentPlan:
    client_id: Optional[str] = None


@strawberry_sqlalchemy_mapper.type(PayKeeperPaymentDataTable)
class PayKeeperPaymentDataIn:
    user_payment: Optional[UserPayment]


@strawberry_sqlalchemy_mapper.type(UserDocumentRequestTable)
class UserDocumentRequest:
    client_id: Optional[str] = None
    user: Optional[User] = None
    medical_center: Optional[MedicalCenter] = None


strawberry_sqlalchemy_mapper.finalize()
