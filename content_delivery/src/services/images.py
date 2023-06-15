import random
from functools import lru_cache
from http import HTTPStatus
from typing import Optional

from db.cache import Cache, get_cache
from db.database import DataStorage, get_data_storage
from fastapi import Depends, HTTPException
from models.images import Image, Category
from schemas.images import ImageSchema
from sqlalchemy.orm import joinedload
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ImageService:
    def __init__(self, db: DataStorage, cache: Cache) -> None:
        self.db = db
        self.cache = cache

    @staticmethod
    def _sqlalchemy_to_pydantic(image: Image) -> Optional[ImageSchema]:
        """
            A function that converts
            the SQLAlchemy model into a Pydantic schema.

            Args:
                image (Image): The SQLAlchemy model

            Returns:
                image_schema (ImageSchema): The Pydantic schema
        """
        if not image:
            return None

        image_schema = ImageSchema(
            id=str(image.id),
            url=image.url,
            repetitions=image.repetitions,
            categories=[category.name for category in image.categories]
        )

        return image_schema

    async def _get_non_cached_image(
        self,
        images: list[Image]
    ) -> Optional[Image]:
        """
            This function allows you to retrieve an image
            that is not stored in the cache.
            This is necessary to provide a mechanism
            that reduces the probability
            of the same image being output multiple times in succession.

            Args:
                images (list[Image]): The list of Images

            Returns:
                image (Optional[Image]): An image that is not in the cache.
        """
        for image in images:
            is_cached = await self.cache.get(f"{image.id}")
            if not is_cached:
                return image

        return None

    async def _get_images_by_category(
        self,
        session: AsyncSession,
        categories: Optional[list[str]]
    ) -> list:
        images = None

        images = await session.execute(select(Image).filter(
            Image.categories.any(Category.name.in_(categories)),
            Image.repetitions > 0
        ).options(joinedload(Image.categories)))

        images = [image[0] for image in images.unique().all()]  # type: ignore

        return images  # type: ignore

    async def _get_images_by_random(self, session: AsyncSession) -> list:
        images = None

        images = await session.execute(select(Image).filter(
            Image.repetitions > 0
        ).order_by(func.random()).options(joinedload(Image.categories)))

        images = [image[0] for image in images.unique().all()]  # type: ignore

        return images  # type: ignore

    async def get_image(
        self,
        categories: Optional[list[str]]
    ) -> Optional[ImageSchema]:
        """
            A function that allows you to get an image to be shown to the user
            by one of the specified categories.
            If no category is specified, the user receives a random image.
            A caching mechanism is provided which reduces the probability
            that the same image will be shown several times in a row.
            Also, if no picture matching the category is found,
            a random picture is displayed.

            Args:
                categories (Optional[list[str]]):
                    The list of categories by which the image is searched

            Returns:
                image (ImageSchema) Response model of Image
        """
        images = None
        result = None

        async with self.db.get_session() as session:
            if categories:
                images = await self._get_images_by_category(
                    session,
                    categories
                )

            if not categories or not images:
                images = await self._get_images_by_random(session)

            if not images:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail='Images are not found'
                )
            else:
                result = await self._get_non_cached_image(images)
                if not result:
                    result = random.choice(images)

            result.repetitions -= 1
            await self.cache.set(f"{result.id}", "True")

        return ImageService._sqlalchemy_to_pydantic(result)


@lru_cache()
def get_film_service(
        data_storage: DataStorage = Depends(get_data_storage),
        cache: Cache = Depends(get_cache)
) -> ImageService:
    return ImageService(data_storage, cache)
