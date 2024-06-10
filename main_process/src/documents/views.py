import re
from fastapi import APIRouter, HTTPException, Security, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.authorization.auth import Auth
from core.config.responses import response_401, response_404, response_422, response_500
from core.smb_connector.smb_connector import get_file_by_smb


security = HTTPBearer()
views = APIRouter()
auth = Auth()


@views.post('/get_file',
            summary='Получить выбранный файлы',
            responses={401: response_401, 404: response_404, 422: response_422, 500: response_500}
)
async def export_user_file(*, file_link: str,
                           credentials: HTTPAuthorizationCredentials = Security(security)
                          ):
    """Получение из МИС файла по ранее полученной текстовой ссылке"""

    auth_token = credentials.credentials

    # Авторизация
    user = await auth.token_auth(auth_token)

    if not user:
        raise HTTPException(status_code=403, detail='Пользователь не авторизован')

    # Скачиваем файл
    data = await get_file_by_smb(file_link)

    if isinstance(data, list):
        raise HTTPException(status_code=data[0], detail=data[2])

    # Определяем имя файла
    m = re.search(r"(\d+[..]\w+\b)", file_link)
    file_name = m.group(0)

    response = Response(
        content=data, headers={'Content-Disposition': f'attachment; filename="{file_name}"',
                               'Access-Control-Expose-Headers': 'Content-Disposition'},
        media_type="application/octet-stream"
    )

    return response
