from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional

from models.images import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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

    def connect(self, dsn):
        self._db_engine = create_engine(dsn)
        self._session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._db_engine
        )

    def db_init(self):
        self._base.metadata.create_all(self._db_engine)

    @contextmanager
    def get_session(self):
        try:
            session = self._session()
            yield session
            session.commit()
        except Exception:
            session.rollback()

    def disconnect(self):
        self._session.close_all()


data_storage: Optional[DataStorage] = None


async def get_data_storage() -> Optional[DataStorage]:
    return data_storage
