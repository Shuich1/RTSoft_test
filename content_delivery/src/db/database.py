from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Optional

from models.images import Base
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class DataStorage(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def db_init(self):
        pass

    @abstractmethod
    def get_session(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass


class SQLAlchemyDataStorage(DataStorage):
    def __init__(self) -> None:
        self._db_engine = None
        self._session = None
        self._base = Base

    async def connect(self, dsn):
        self._db_engine = create_async_engine(dsn)
        self._session = async_sessionmaker(
            autoflush=False,
            bind=self._db_engine,
            expire_on_commit=False
        )

    async def db_init(self):
        async with self._db_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self):
        async with self._session() as session:
            yield session
            await session.commit()

    async def disconnect(self):
        await self._db_engine.dispose()


data_storage: Optional[DataStorage] = None


async def get_data_storage() -> Optional[DataStorage]:
    return data_storage
