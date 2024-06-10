from accounts.config.settings import DEBUG
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from common.config.db import Settings


TOKEN_EXP_TIME = 30

load_dotenv()

settings = Settings()
settings.Config.env_file = "/code/accounts/.env"

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=DEBUG, pool_size=150, max_overflow=150,
                             connect_args={"server_settings": {'timezone': 'UTC'}})
Base = declarative_base()
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
