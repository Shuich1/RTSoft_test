from .base import BaseOrjsonModel


class ImageSchema(BaseOrjsonModel):
    id: str
    url: str
    repetitions: int
    categories: list[str]
