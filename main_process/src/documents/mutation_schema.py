import strawberry
import hashlib
import json
from typing import Optional
from strawberry.types import Info
from strawberry.file_uploads import Upload
# from kafka import KafkaProducer

from core.config.cache_connector import CacheConnector
from core.authorization.auth import Auth
from core.authorization.permissions import (IsAuthenticated,
                                            get_auth_token_by_auth_header)
# from .scalars import DocParams


hasher= hashlib.sha256
cache = CacheConnector()
auth = Auth()


@strawberry.type
class MutationMainProcessDocument:

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def test(
        self,
        info:Info,
        ) -> str:
        """
        Запрос
        """

        user, _ = await get_auth_token_by_auth_header(info)



        return 'result'
