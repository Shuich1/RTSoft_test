from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional

from models.images import Base, Image, Category
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker


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

    def get_images_by_category(
        self,
        session: Session,
        categories: Optional[list[str]]
    ) -> list:
        images = None

        images = session.query(Image).filter(
            Image.categories.any(Category.name.in_(categories)),
            Image.repetitions > 0
        ).all()

        return images

    def get_images_by_random(self, session: Session) -> list:
        images = None

        images = session.query(Image).filter(
            Image.repetitions > 0
        ).order_by(func.random()).all()

        return images


data_storage: Optional[DataStorage] = None


async def get_data_storage() -> Optional[DataStorage]:
    return data_storage
