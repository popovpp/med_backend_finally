from fastapi import APIRouter

from main_process.src import documents


api_router = APIRouter()

api_router.include_router(documents.router, prefix='/documents', tags=['Documents'])
