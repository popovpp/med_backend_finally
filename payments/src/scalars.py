import strawberry
from datetime import datetime, date
from typing import Optional, List

from core.config.scalars import (RequestResult, MedicalCenterIn, UserPaymentIn,
                                 UserIn, PolicyIn, ShifrIn, PaymentTypeIn, ServiceIn,
                                 UserServiceCartIn, AccessTicketIn, DoctorMedicalCenterIn,
                                 ComplexServiceIn, UserPurchaseIn, RefuseReasonIn, PriceIn)
from core.config.mapped_scalars import (MedicalCenter, UserPayment, UserServiceCart,
                                        User, Service)


@strawberry.input
class UserServiceCartInputMut:
    service_id: int
    medical_center_id: int
    access_ticket_id: int
    doctor_mcenter_id: int
    quantity: Optional[int] = 1
    price_id: int


@strawberry.type
class PaymentInfo:
    pay_amount: float
    user_id: str
    user_payment_id: int
    user_email: str
    user_phone_number: str
    invoice_id: Optional[str] = None


@strawberry.type
class ServicePaymentInfo:
    name: str
    price: float
    quantity: int
    sum: float
    tax: Optional[float] = None


@strawberry.type
class PaynemtData:
    services_payment_list: Optional[List[ServicePaymentInfo]] = None
    payment_info: Optional[PaymentInfo] = None


@strawberry.type
class PaymentDataResult(RequestResult):
    data: Optional[PaynemtData] = None


@strawberry.type
class UserServicesForOracle:
    service_client_id: Optional[str] = None
    user_client_id: Optional[str] = None
    policy_client_id: Optional[str] = None
    medical_center_client_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    complex_service_id: Optional[int] = None
    complex_service_status: Optional[int] = None
    service_status: Optional[int] = None
    quantity: Optional[int] = None
    stac_satus: Optional[bool] = None
    cito_status: Optional[bool] = None
    refuse_date: Optional[datetime] = None
    refuse_reason_text: Optional[str] = None
    description: Optional[float] = None
    discount: Optional[float] = None
    discount_coefficient: Optional[float] = None
    price_client_id: Optional[str] = None
    user_purchase_id: Optional[int] = None
    shifr_client_id: Optional[str] = None
    access_ticket_client_id: Optional[str] = None
    doctor_mcenter_client_id: Optional[str] = None
    doctor_send_id: Optional[int] = None
    doctor_exec_id: Optional[int] = None
    doctor_nurse_id: Optional[int] = None
    doctor_paramedic_id: Optional[int] = None


@strawberry.type
class UserPaymentForOracle:
    # В строку через запятую без пробелов
    user_service_cart_client_ides: Optional[str] = None
    patient_client_id: Optional[str] = None
    policy_client_id: Optional[str] = None
    shifr_client_id: Optional[str] = None
    payment_type_client_id: Optional[str] = None
    medical_center_client_id: Optional[str] = None
    # В строку через запятую без пробелов
    advance_user_payment_cliend_ides: Optional[str] = None
    advance_amount: Optional[float] = None
    payment_date: Optional[str] = None


@strawberry.input
class UserServiceCartInputAdv(UserServiceCartInputMut):
    service_id: Optional[int] = None
    medical_center_id: Optional[int] = None
    access_ticket_id: Optional[int] = None
    doctor_mcenter_id: Optional[int] = None
    quantity: int
    price_id: Optional[int] = None


@strawberry.input
class MedicalCenterInputPay(MedicalCenterIn):
    id: Optional[List[int]] = None


@strawberry.type
class McentersUnuseAdvancesSum:
    medical_centers: list[MedicalCenter]
    unused_advances_sum: float


@strawberry.type
class McentersUnuseAdvancesSumResult(RequestResult):
    data: Optional[list[McentersUnuseAdvancesSum]] = None


@strawberry.input
class UserPaymentInputPay(UserPaymentIn):
    id: Optional[List[int]] = None
    user: Optional[UserIn] = None
    policy: Optional[PolicyIn] = None
    shifr: Optional[ShifrIn] = None
    payment_type: Optional[PaymentTypeIn] = None
    linked_user_payment: Optional['UserPaymentInputPay'] = None


@strawberry.type
class UserPaymentWithServices:
    payment: Optional[UserPayment] = None
    services_names: Optional[List[str]] = None
    medical_center: Optional[MedicalCenter] = None


@strawberry.type
class UserPaymentResultPay(RequestResult):
    data: Optional[List[UserPaymentWithServices]] = None


@strawberry.input
class UserServiceCartInputPay(UserServiceCartIn):
    id: Optional[List[int]] = None
    service: Optional[ServiceIn] = None
    user: Optional[UserIn] = None
    shifr: Optional[ShifrIn] = None
    policy: Optional[PolicyIn] = None
    medical_center: Optional[MedicalCenterIn] = None
    access_ticket: Optional[AccessTicketIn] = None
    doctor_mcenter: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_exec: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_send: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_nurse: Optional[DoctorMedicalCenterIn] = None
    # doctor_mcenter_paramedic: Optional[DoctorMedicalCenterIn] = None
    complex_service: Optional[ComplexServiceIn] = None
    user_purchase: Optional[UserPurchaseIn] = None
    refuse_reason: Optional[RefuseReasonIn] = None
    price: Optional[PriceIn] = None


@strawberry.type
class ServiceCurrentDebt:
    user: Optional[User] = None
    medical_center: Optional[MedicalCenter] = None
    service_in_cart: Optional[UserServiceCart] = None
    debt: Optional[float] = None
    payment_id: Optional[int] = None


@strawberry.type
class ServiceCurrentDebtResult(RequestResult):
    data: Optional[List[ServiceCurrentDebt]]


@strawberry.type
class ServicesDebt:
    services_medical_center: Optional[MedicalCenter] = None
    services_debt: Optional[float] = None


@strawberry.type
class CurrentDebt:
    user: Optional[User] = None
    services_debt_list: Optional[List[ServicesDebt]] = None
    sum_services_debt: Optional[float] = None
    subscribe_debt: Optional[float] = None
    sum_debt: Optional[float] = None


@strawberry.type
class CurrentDebtResult(RequestResult):
    data: Optional[List[CurrentDebt]] = None


@strawberry.type
class PaymentsWithServices:
    payment_date: Optional[date] = None
    payment_id: Optional[int] = None
    user_id: Optional[int] = None
    payment_type: Optional[str] = None
    service: Optional[Service] = None
    amount: Optional[float] = None


@strawberry.type
class  HistoryPaymentsResult(RequestResult):
    data: Optional[List[PaymentsWithServices]] = None


@strawberry.type
class InitproClient:
    email: str
    phone: str


@strawberry.type
class InitproCompany:
    email: str
    sno: str
    inn: str
    payment_address: str


@strawberry.type
class InitproItemVat:
    type: str
    sum: float


@strawberry.type
class InitproItem:
    name:str
    price: float
    quantity: int
    sum: float
    payment_method: str
    payment_object: str
    vat: InitproItemVat


@strawberry.type
class InitproPayment:
    type: int
    sum: float


@strawberry.type
class InitproVat:
    type: str
    sum: float


@strawberry.type
class InitproReceipt:
    client: InitproClient
    company: InitproCompany
    items: List[InitproItem]
    payments: List[InitproPayment]
    vats: List[InitproVat]
    total: float


@strawberry.type
class InitproRegistrationPayload:
    external_id: str
    receipt: InitproReceipt
    timestamp: str


@strawberry.input
class DocParams:
    doc_client_id: str
    doc_params: str
    service_client_id: str


@strawberry.input
class UserServiceCartInputDoc:
    service_id: int
    medical_center_id: int
    access_ticket_id: Optional[int] = None
    doctor_mcenter_id: Optional[int] = None
    quantity: Optional[int] = 1
    price_id: Optional[int] = None
