import strawberry
from typing import Optional, List
from datetime import date, datetime

from core.config.mapped_scalars import (MedicalCenter, User, UserServiceCart,
                                        Service, DoctorMedicalCenter, ComplexService,
                                        Shifr, Policy, UserPurchase, Price, RefuseReason,
                                        AccessTicket)
from core.config.scalars import (RequestResult, MedicalCenterIn,
                                 ServiceIn,
                                 PriceIn, DoctorMedicalCenterIn, ComplexServiceIn,
                                 ShifrIn, PolicyIn, UserIn, UserPurchaseIn, RefuseReasonIn,UserServiceCartIn,
                                 AccessTicketIn, UserServiceCartOut)


@strawberry.type
class UserServiceCartResult(RequestResult):
    data: Optional[List[UserServiceCart]]


@strawberry.input
class UserServiceCartInput(UserServiceCartIn):
    id: Optional[List[int]] = None
    service: Optional[ServiceIn] = None
    user: Optional[UserIn] = None
    shifr: Optional[ShifrIn] = None
    policy: Optional[PolicyIn] = None
    medical_center: Optional[MedicalCenterIn] = None
    access_ticket: Optional[AccessTicketIn] = None
    doctor_mcenter: Optional[DoctorMedicalCenterIn] = None
    doctor_mcenter_exec: Optional[DoctorMedicalCenterIn] = None
    doctor_mcenter_send: Optional[DoctorMedicalCenterIn] = None
    doctor_mcenter_nurse: Optional[DoctorMedicalCenterIn] = None
    doctor_mcenter_paramedic: Optional[DoctorMedicalCenterIn] = None
    complex_service: Optional[ComplexServiceIn] = None
    user_purchase: Optional[UserPurchaseIn] = None
    refuse_reason: Optional[RefuseReasonIn] = None
    price: Optional[PriceIn] = None


@strawberry.type
class UserServiceCartOutput(UserServiceCartOut):
    id: Optional[int] = None
    service: Optional[Service] = None
    user: Optional[User] = None
    shifr: Optional[Shifr] = None
    policy: Optional[Policy] = None
    medical_center: Optional[MedicalCenter] = None
    access_ticket: Optional[AccessTicket] = None
    doctor_mcenter: Optional[DoctorMedicalCenter] = None
    doctor_mcenter_exec: Optional[DoctorMedicalCenter] = None
    doctor_mcenter_send: Optional[DoctorMedicalCenter] = None
    doctor_mcenter_nurse: Optional[DoctorMedicalCenter] = None
    doctor_mcenter_paramedic: Optional[DoctorMedicalCenter] = None
    complex_service: Optional[ComplexService] = None
    user_purchase: Optional[UserPurchase] = None
    refuse_reason: Optional[RefuseReason] = None
    price: Optional[Price] = None


@strawberry.type
class UserServiceCartOutputResult(RequestResult):
    data: Optional[List[UserServiceCartOutput]]


@strawberry.input
class UserServiceCartInputMut:
    service_id: int
    medical_center_id: int
    access_ticket_id: Optional[int] = None
    doctor_mcenter_id: int
    quantity: Optional[int] = 1
    price_id: int


@strawberry.type
class UserServiceCartOutputCache:
    id: Optional[int] = None
    access_ticket_id: Optional[int] = None
    access_ticket_ticket_datetime: Optional[datetime] = None
    service_id: Optional[int] = None
    service_name_for_lk: Optional[str] = None
    quantity: Optional[int] = None
    medical_center_id: Optional[int] = None
    medical_center_name: Optional[str] = None
    medical_center_address: Optional[str] = None
    doctor_mcenter_id: Optional[int] = None
    doctor_mcenter_fio: Optional[str] = None
    doctor_mcenter_mposition_view_name: Optional[str] = None
    price_id: Optional[int] = None
    price_nal: Optional[float] = None    
    user_id: Optional[int] = None


@strawberry.type
class UserServiceCartOutputCacheResult(RequestResult):
    data: Optional[List[UserServiceCartOutputCache]]
