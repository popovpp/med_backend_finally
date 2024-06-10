import strawberry
from typing import Optional, List
from datetime import date

from core.config.scalars import (MedicalCenterIn, ServiceTypeIn, CityIn, MedicalPositionIn, ServiceIn,
                                 MedicalSpecialityIn, DoctorIn, DoctorMspecialityIn, DoctorServiceIn,
                                 PriceIn, DoctorScheduleIn, StaffTypeIn, DoctorCategoryIn, DoctorStatusTypeIn,
                                 DoctorStatusIn, PatientTypeIn, DoctorMedicalCenterIn, DoctorPatientTypeIn,
                                 ServiceMedicalSpecialityIn, ComplexServiceIn, ComplexServiceItemIn,
                                 FinancialTypeIn, ShifrIn, PolicyIn, UserSubscribeIn, DoctorReplacementIn,
                                 SubscribeDoctorIn, PackTypeIn, SubscribeServicePackIn, SubscribeSpackRecordIn,
                                 ShifrDiscountPeriodIn, PricePeriodIn, PriceNameIn, PaymentTypeIn, UserPaymentIn,
                                 UserPurchaseReturnIn, RefuseReasonIn, UserServiceCartIn, UserServicePlanIn,
                                 AccessTicketIn, RequestResult, UserAdminIn, RelationshipDegreesIn, UserRelativeIn,
                                 UserIn, DoctorMedicalCenterServiceIn, MedicalCenterPriceNameIn, UserDefaultObjectIn)
from core.config.mapped_scalars import UserAdmin, UserRelative


@strawberry.input
class CityInputAdm(CityIn):
    name: str
    is_active: Optional[bool] = True


@strawberry.input
class MedicalCenterInputAdm(MedicalCenterIn):
    city_id: int
    name: str
    address: str
    inn: str
    bank_bic: str
    settlement_account: str
    correspondent_account: str
    kpp: str
    phone_fax: str
    work_time: str


@strawberry.input
class ServiceTypeInputAdm(ServiceTypeIn):
    pass


@strawberry.input
class MedicalPositionInputAdm(MedicalPositionIn):
    is_active: Optional[bool] = True


@strawberry.input
class StaffTypeInputAdm(StaffTypeIn):
    is_active: Optional[bool] = True


@strawberry.input
class DoctorCategoryInputAdm(DoctorCategoryIn):
    is_active: Optional[bool] = True


@strawberry.input
class DoctorStatusTypeInputAdm(DoctorStatusTypeIn):
    is_active: Optional[bool] = True


@strawberry.input
class ServiceInputAdm(ServiceIn):
    pass


@strawberry.input
class MedicalSpecialityInputAdm(MedicalSpecialityIn):
    view_name: str
    search_name: str


@strawberry.input
class DoctorInputAdm(DoctorIn):

    first_name: str
    last_name: str
    is_active: Optional[bool] = True


@strawberry.input
class DoctorMspecialityInputAdm(DoctorMspecialityIn):
    pass


@strawberry.input
class DoctorServiceInputAdm(DoctorServiceIn):
    pass


@strawberry.input
class PriceInputAdm(PriceIn):
    pass


@strawberry.input
class DoctorScheduleInputAdm(DoctorScheduleIn):
    pass


@strawberry.input
class DoctorStatusInputAdm(DoctorStatusIn):
    pass


@strawberry.input
class PatientTypeInputAdm(PatientTypeIn):
    pass


@strawberry.input
class DoctorMedicalCenterInputAdm(DoctorMedicalCenterIn):
    pass


@strawberry.input
class DoctorPatientTypeInputAdm(DoctorPatientTypeIn):
    pass


@strawberry.input
class ServiceMedicalSpecialityInputAdm(ServiceMedicalSpecialityIn):
    pass


@strawberry.input
class ComplexServiceInputAdm(ComplexServiceIn):
    pass


@strawberry.input
class ComplexServiceItemInputAdm(ComplexServiceItemIn):
    pass


@strawberry.input
class FinancialTypeInputAdm(FinancialTypeIn):
    pass


@strawberry.input
class ShifrInputAdm(ShifrIn):
    pass


@strawberry.input
class PolicyInputAdm(PolicyIn):
    pass


@strawberry.input
class UserSubscribeInputAdm(UserSubscribeIn):
    pass


@strawberry.input
class DoctorReplacementInputAdm(DoctorReplacementIn):
    pass


@strawberry.input
class SubscribeDoctorInputAdm(SubscribeDoctorIn):
    pass


@strawberry.input
class PackTypeInputAdm(PackTypeIn):
    pass


@strawberry.input
class SubscribeServicePackInputAdm(SubscribeServicePackIn):
    pass


@strawberry.input
class SubscribeSpackRecordInputAdm(SubscribeSpackRecordIn):
    pass


@strawberry.input
class ShifrDiscountPeriodInputAdm(ShifrDiscountPeriodIn):
    pass


@strawberry.input
class ShifrDiscountInputAdm(ShifrDiscountPeriodIn):
    pass


@strawberry.input
class PricePeriodInputAdm(PricePeriodIn):
    pass


@strawberry.input
class PriceNameInputAdm(PriceNameIn):
    pass


@strawberry.input
class PaymentTypeInputAdm(PaymentTypeIn):
    pass


@strawberry.input
class UserPaymentInputAdm(UserPaymentIn):
    pass


@strawberry.input
class UserPurchaseReturnInputAdm(UserPurchaseReturnIn):
    pass


@strawberry.input
class RefuseReasonInputAdm(RefuseReasonIn):
    pass


@strawberry.input
class UserServiceCartInputAdm(UserServiceCartIn):
    pass


@strawberry.input
class UserServicePlanInputAdm(UserServicePlanIn):
    pass


@strawberry.input
class AccessTicketInputAdm(AccessTicketIn):
    pass


@strawberry.type
class UserAdminResult(RequestResult):
    data: Optional[list[UserAdmin]]


@strawberry.input
class UserAdminInputAdm(UserAdminIn):
    id: Optional[int] = None


@strawberry.input
class RelationshipDegreesInputAdm(RelationshipDegreesIn):
    id: Optional[int] = None


@strawberry.input
class UserRelativeInputAdm(UserRelativeIn):
    id: Optional[int] = None
    user: Optional[UserIn] =None
    relative: Optional[UserIn] = None
    relationship_degree: Optional[RelationshipDegreesIn] = None


@strawberry.type
class UserRelativeResultAdm(RequestResult):
    data: Optional[List[UserRelative]]


@strawberry.input
class DoctorMedicalCenterServiceInputAdm(DoctorMedicalCenterServiceIn):
    id: Optional[int] = None
    service: Optional[ServiceIn] = None
    doctor_mcenters: Optional[DoctorMedicalCenterIn] = None


@strawberry.input
class MedicalCenterPriceNameInputAdm(MedicalCenterPriceNameIn):
    id: Optional[int] = None
    medical_center: Optional[MedicalCenterIn] = None
    price_name: Optional[PriceNameIn] = None
    service_type: Optional[ServiceTypeIn] = None


@strawberry.input
class UserDefaultObjectInputAdm(UserDefaultObjectIn):
    id: Optional[int] = None
    payment_advance: Optional[UserPaymentIn]
