import strawberry
from datetime import date
from strawberry.types import Info
from typing import Optional


from core.config.cache_connector import CacheConnector
from core.authorization.permissions import (IsAuthenticated, get_auth_user_by_auth_header)
from core.sa_tables.main_process import (UserDefaultObjectTable)
from core.sa_tables.accounts import UserTable
from core.src.common_resolvers import getting_objs, getting_relatives_ids
from core.config.scalars import UserDefaultObjectIn, UserIn

from .resolvers import (getting_patient_files, getting_list_of_available_docs,
                        getting_list_of_requested_docs, getting_patient_protocols,
                        getting_patient_protocol_content)
from .scalars import (UserFileResult, AvailableDocsResult, UserDocumentRequestResult,
                      PatientProtocolsResult, ProtocolContentResult)


cache = CacheConnector()


@strawberry.type
class QueryMainProcessDocument:

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_patient_files(self,
                                info:Info
                                ) -> UserFileResult:

        """Получение ссылок на файлы пациента"""

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        default_obj_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(
            info, user, UserDefaultObjectTable,
            default_obj_filtering_attrs
        )
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        result_list = await getting_patient_files(patient)

        return result_list

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_list_of_available_docs(self,
                                         info:Info
                                         ) -> AvailableDocsResult:

        """Получение списка доступных докуентов"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list = await getting_list_of_available_docs()

        return result_list

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_list_of_requested_docs(self,
                                         info:Info
                                         ) -> UserDocumentRequestResult:

        """Получение списка запрошенных докуентов"""

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        default_obj_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(
            info, user, UserDefaultObjectTable,
            default_obj_filtering_attrs
        )
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        result_list = await getting_list_of_requested_docs(patient)

        return result_list

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_patient_protocols(self,
                                    info:Info,
                                    start_date: date,
                                    end_date: date,
                                    patient_id: Optional[int] = None
                                    ) -> PatientProtocolsResult:

        """Получение списка протоколов пациента"""

        user, _ = await get_auth_user_by_auth_header(info)

        if start_date > end_date:
            return PatientProtocolsResult(
                status_code=422,
                details="The start date can't be more than the end date.",
                details_ru="Начальная дата не может быть больше, че конечная."
            )

        if (end_date - start_date).days >365:
            return PatientProtocolsResult(
                status_code=422,
                details="The end date can't be more than the start date more than to 365 days.",
                details_ru="Конечная дата не может превышать начальную ьольше, чем на 365 дней."
            )

        # Получаем айдишники всех родственников
        relatives_ids = await getting_relatives_ids(user.id)
        relatives_ids.append(user.id)

        if patient_id:
            if patient_id not in relatives_ids:
                return PatientProtocolsResult(
                    status_code=422,
                    details=f'The patient {patient_id} is not your relative',
                    details_ru=f'Пациент {patient_id} не является вашим родственником'
                )

        # Получаем указанного пациента
        if patient_id:
            user_filtering_attrs = UserIn(
                id = patient_id
            )
            patient_objs, _, _ = await getting_objs(
                info,
                user,
                UserTable,
                user_filtering_attrs
            )
        else:
            patient_objs = None

        # Получаем пациента по умолчанию
        default_obj_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(
            info, user, UserDefaultObjectTable,
            default_obj_filtering_attrs
        )

        if patient_objs:
            patient = patient_objs[0]
        else:
            patient = user_default_objs[0].default_patient

        print(patient.id)

        result_list = await getting_patient_protocols(patient,
                                                      start_date=start_date,
                                                      end_date=end_date)

        return result_list

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_patient_protocol_content(self,
                                            info:Info,
                                            patient_protocol_client_id: str
                                            ) -> ProtocolContentResult:

        """Получение заданного протокола пациента пациента"""

        result_content = await getting_patient_protocol_content(patient_protocol_client_id)

        return result_content
