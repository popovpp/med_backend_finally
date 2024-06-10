from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, validator
from dotenv import load_dotenv

from .settings import DEBUG

TOKEN_EXP_TIME = 30

load_dotenv()

class Settings(BaseSettings):
    PG_SERVER: str
    PG_USER: str
    PG_PASSWORD: str
    PG_DB: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("PG_USER"),
            password=values.get("PG_PASSWORD"),
            host=values.get("PG_SERVER"),
            port=values.get("PG_PORT"),
            path=f"/{values.get('PG_DB') or  ''}",
        )

    class Config:
        case_sensitive = True
        env_file = "/code/common/.env"


settings = Settings()

sync_engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=DEBUG, poolclass=NullPool,
                             connect_args={"server_settings": {'timezone': 'UTC'}})
Base = declarative_base()
metadata = Base.metadata
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.close()
