import strawberry
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from strawberry.fastapi import GraphQLRouter
from logging import getLogger
from logging.config import dictConfig

from config.logger import logger
from config.metadata import tags_metadata
from config.routers import api_router
from config.settings import PROJECT_TITLE, PROJECT_VERSION, DEBUG, PROJECT_DESCRIPTION, APP_URL
from src.query_schema import QueryUser
from src.mutation_schema import MutationUser

from core.config.models import Error, ErrorField


@strawberry.type
class Query(QueryUser):
    pass


@strawberry.type
class Mutation(MutationUser):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    debug=DEBUG,
    openapi_tags=tags_metadata,
    title=PROJECT_TITLE,
    version=PROJECT_VERSION,
    description=PROJECT_DESCRIPTION,
    root_path=APP_URL
)

app.openapi_version = "3.0.0"
app.include_router(api_router)
app.mount('/static', StaticFiles(directory='./static'), name='static')


graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


dictConfig(logger)
logger = getLogger('gunicorn.access')


@app.get('/openapi', include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url='openapi.json',
        title=f'{app.title} - Documentation',
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url=f'static/swagger-ui-bundle.js',
        swagger_css_url=f'static/swagger-ui.css',
    )


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):

    errors = []
    for i in exc.errors():

        try:
            field = i['loc'][-1]
        except:
            field = 'unknown'

        try:
            message = i['msg'].capitalize()
        except:
            message = ''
        error_field = ErrorField(field=field, message=message)
        errors.append(error_field)

    error = Error(detail='Ошибка', errors=errors)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error.dict(),
    )


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    elapsed = datetime.now() - start_time
    logger.info(f'Process time: {int(elapsed.total_seconds() * 1000)} ms - "{request.url}"')
    return response
