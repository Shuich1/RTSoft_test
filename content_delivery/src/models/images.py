from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid
from typing import Any

Base: Any = declarative_base()


class Image(Base):
    __tablename__ = 'image'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String)
    repetitions = Column(Integer)

    categories = relationship(
        'Category',
        secondary='image_category',
        back_populates='images'
    )


class Category(Base):
    __tablename__ = 'category'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)

    images = relationship(
        'Image',
        secondary='image_category',
        back_populates='categories'
    )


class ImageCategoryAssociation(Base):
    __tablename__ = 'image_category'
    image_id = Column(
        UUID(as_uuid=True),
        ForeignKey('image.id'),
        primary_key=True
    )
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey('category.id'),
        primary_key=True
    )
