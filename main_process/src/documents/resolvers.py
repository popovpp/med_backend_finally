import xmltodict
import json
from sqlalchemy.future import select as async_select
from sqlalchemy import or_
from datetime import datetime, timedelta

from core.config.cache_connector import CacheConnector
from core.config.db import get_session
from core.sa_tables.main_process import UserDocumentRequestTable
from core.sa_tables.accounts import MedicalCenterTable
from oracle_connector.config.settings import (ORACLE_PROC_GET_PATIENT_FILES,
                                              ORACLE_PROC_GET_LIST_OF_AVALAIBLE_DOCS,
                                              ORACLE_PROC_GET_LIST_OF_REQUIRED_FILES,
                                              ORACLE_PROC_GET_PATIENT_PROTOCOLS,
                                              ORACLE_PROC_P_TEST)
from oracle_connector.scripts.oracle_connector import call_oracle_proc_for_list_result

from .scalars import (UserFileResult, UserFile, AvailableDocsResult, AvailableDoc,
                      UserDocumentRequestResult, PatientProtocolsResult,
                      PatientProtocol, ProtocolContentResult)


cache = CacheConnector()


async def getting_patient_files(patient):

    # Получение ссылок на файлы пациента для скачивания
    try:
        data_for_oracle = [str(patient.client_id)]
        status_code, oracle_set_result = await call_oracle_proc_for_list_result(data_for_oracle, ORACLE_PROC_GET_PATIENT_FILES)
        print(oracle_set_result)
        if status_code == 200:
            result_list = []
            for item in oracle_set_result:
                result_list.append(
                    UserFile(
                        document_client_id=str(item[1]),
                        document_date=item[2],
                        user_id=patient.id,
                        document_name=item[7],
                        document_link=item[9][8:] if item[9] else None
                    )
                )
            return UserFileResult(
                data=result_list,
                details='Ok',
                details_ru='Ок',
                status_code=status_code
            )
        elif status_code == 500:
            return UserFileResult(
                status_code=500,
                details_ru='Функция временно недоступна',
                details=str(oracle_set_result)
            )
        elif status_code == 404:
            return UserFileResult(
                status_code=status_code,
                details_ru='У пользователя нет документов для скачивания',
                details=str(oracle_set_result)
            )
        else:
            return UserFileResult(
                status_code=500,
                details_ru=f'Процедура Oracle {ORACLE_PROC_GET_PATIENT_FILES} отработала некорректно, сообщите администратору.',
                details=str(oracle_set_result)
            )
    except Exception as e:
        print(e)
        return UserFileResult(
            status_code=500,
            details=f"{str(oracle_set_result)}, {e} - The call of Oracle has been failed.",
            details_ru=f"{str(oracle_set_result)}, {e} - Сбой вызова процедуры Oracle."
        )


async def getting_list_of_available_docs():

    data_for_oracle = []
    status_code, oracle_set_result = await call_oracle_proc_for_list_result(
        data_for_oracle, ORACLE_PROC_GET_LIST_OF_AVALAIBLE_DOCS
    )

    if status_code != 200:
        return AvailableDocsResult(
            status_code=status_code,
            details='Calling of ORACLE_PROC_GET_LIST_OF_AVALAIBLE_DOCS was failed.',
            details_ru=f'Вызов процедуры Oracle потерпел неудачу - {oracle_set_result}.'
        )
    else:
        avalaible_docs_list = []
        for item in oracle_set_result:
            item_3 = xmltodict.parse(item[3].lower())
            for elem in item_3['data']['paremeters']['param']:
                elem['value'] = None
            if item[4] == 1:
                doc = AvailableDoc(
                    doc_client_id=item[1],
                    doc_name=item[2],
                    doc_params=json.dumps(item_3['data']['paremeters'], ensure_ascii=False),
                    is_active=item[4],
                    service_client_id=item[5],
                    available_mc=item_3['data']['available']['mc'],
                    available_email=item_3['data']['available']['email']
                )
                avalaible_docs_list.append(doc)

        return AvailableDocsResult(
            data=avalaible_docs_list,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )


async def getting_list_of_requested_docs(patient):

    today = datetime.now()

    data_for_oracle = [str(patient.client_id)]
    status_code, oracle_set_result = await call_oracle_proc_for_list_result(
        data_for_oracle, ORACLE_PROC_GET_LIST_OF_REQUIRED_FILES
    )

    if status_code != 200:
        return AvailableDocsResult(
            status_code=status_code,
            details='Calling of ORACLE_PROC_GET_LIST_OF_AVALAIBLE_DOCS was failed.',
            details_ru=f'Вызов процедуры Oracle потерпел неудачу - {oracle_set_result}.'
        )
    else:
        async with get_session() as s:
            request_records = (await s.execute(async_select(
                UserDocumentRequestTable
            ).filter(
                UserDocumentRequestTable.user_id == patient.id,
                UserDocumentRequestTable.is_requested == True,
                UserDocumentRequestTable.client_id != None,
                or_(
                    UserDocumentRequestTable.status != 3,
                    UserDocumentRequestTable.status == None
                )
            ))).scalars().all()

            for item in oracle_set_result:
                for record in request_records:
                    if record.client_id == item[1]:
                        if not record.doc_name:
                            record.doc_name = item[6]
                        if not record.medical_center_id:
                            record.medical_center_id = (await s.execute(async_select(
                                MedicalCenterTable.id
                            ).filter(
                                MedicalCenterTable.client_id == item[7]
                            ))).scalars().one_or_none()
                        if not record.obtaining_method:
                            record.obtaining_method = item[8]
                        record.status = item[9]

                        s.add(record)
                        await s.flush()

            output_result = request_records = (await s.execute(async_select(
                UserDocumentRequestTable
            ).filter(
                UserDocumentRequestTable.is_requested == True,
                UserDocumentRequestTable.client_id != None,
                UserDocumentRequestTable.request_date >= today - timedelta(days=365),
                UserDocumentRequestTable.user_id == patient.id,
            ))).scalars().all()

            await s.commit()

        return UserDocumentRequestResult(
            data=output_result,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )


async def getting_patient_protocols(patient, start_date=None, end_date=None):

    data_for_oracle = [
        patient.client_id,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    ]
    status_code, oracle_set_result = await call_oracle_proc_for_list_result(
        data_for_oracle, ORACLE_PROC_GET_PATIENT_PROTOCOLS
    )

    if status_code != 200:
        return PatientProtocolsResult(
            status_code=status_code,
            details=f'Calling of ORACLE_PROC_GET_LIST_OF_AVALAIBLE_DOCS was failed - {oracle_set_result}.',
            details_ru=f'Вызов процедуры Oracle потерпел неудачу - {oracle_set_result}.'
        )
    else:
        protocols_list = []
        for item in oracle_set_result:
            protocol = PatientProtocol(
                patient_protocol_client_id=item[0],
                protocol_name=item[1],
                protocol_date=item[2],
                doctor_medical_center_client_id=item[3],
                doctor_fio=item[4],
                doctor_medical_speciality_client_id=item[5],
                doctor_medical_speciality_name=item[6],
                access_ticket_client_id=item[7]
            )
            protocols_list.append(protocol)

            protocols_list = sorted(
                protocols_list,
                key=lambda x: datetime.strptime(x.protocol_date, '%d.%m.%Y %H:%M:%S'),
                reverse=True)

        return PatientProtocolsResult(
            data=protocols_list,
            status_code=200,
            details='Ok',
            details_ru='Ок'
        )


async def getting_patient_protocol_content(patient_protocol_client_id):

    data_for_oracle = [
        patient_protocol_client_id,
    ]
    status_code, oracle_set_result = await call_oracle_proc_for_list_result(
        data_for_oracle, ORACLE_PROC_P_TEST
    )

    if status_code != 200:
        return ProtocolContentResult(
            status_code=status_code,
            details=f'Calling of ORACLE_PROC_P_TEST was failed - {oracle_set_result}.',
            details_ru=f'Вызов процедуры Oracle потерпел неудачу - {oracle_set_result}.'
        )
    else:
        return ProtocolContentResult(
            data=oracle_set_result[0][0].read(),
            status_code=status_code,
            details='Ok',
            details_ru='Ок'
        )
