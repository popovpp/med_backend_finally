import strawberry
from datetime import date
from typing import Optional, List

from core.config.scalars import (RequestResult)
from core.config.mapped_scalars import UserDocumentRequest


@strawberry.type
class UserFile:
    document_client_id: Optional[str] = None
    document_date: Optional[str] = None
    user_id: Optional[int] = None
    document_name: Optional[str] = None
    document_link: Optional[str] = None


@strawberry.type
class UserFileResult(RequestResult):
    data: Optional[List[UserFile]] = None


@strawberry.type
class AvailableDoc:
    doc_client_id: str
    doc_name: str
    doc_params: str
    is_active: int
    service_client_id: str
    available_mc: str
    available_email: str


@strawberry.type
class AvailableDocsResult(RequestResult):
    data: Optional[List[AvailableDoc]] = None


@strawberry.type
class UserDocumentRequestResult(RequestResult):
    data: Optional[List[UserDocumentRequest]]


@strawberry.type
class PatientProtocol:
    patient_protocol_client_id: Optional[str] = None
    protocol_name: Optional[str] = None
    protocol_date: Optional[str] = None
    doctor_medical_center_client_id: Optional[str] = None
    doctor_fio: Optional[str] = None
    doctor_medical_speciality_client_id: Optional[str] = None
    doctor_medical_speciality_name: Optional[str] = None
    access_ticket_client_id: Optional[str] =None


@strawberry.type
class PatientProtocolsResult(RequestResult):
    data: Optional[List[PatientProtocol]]


@strawberry.type
class ProtocolContentResult(RequestResult):
    data: Optional[str] = None
