from typing import Annotated

from core.config import templates
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from schemas.images import ImageSchema
from services.images import ImageService, get_film_service

router = APIRouter()


@router.get(
    "/",
    response_model=ImageSchema,
    summary="Получение изображения"
)
async def get_image(
    category: Annotated[list[str] | None, Query()] = None,
    image_service: ImageService = Depends(get_film_service)
):
    return await image_service.get_image(categories=category)


@router.get(
    "/html",
    response_class=HTMLResponse
)
async def get_image_html(
    request: Request,
    category: Annotated[list[str] | None, Query()] = None,
    image_service: ImageService = Depends(get_film_service)
):
    image = await image_service.get_image(categories=category)
    return templates.TemplateResponse(
        "image.html",
        {"request": request, "image": image}
    )
