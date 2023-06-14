from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings, PostgresDsn


class PostgresSettings(BaseSettings):
    postgres_host: str
    postgres_port: str
    postgres_db: str
    postgres_user: str
    postgres_password: str


class Settings(BaseSettings):
    pg_settings = PostgresSettings()
    db: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        user=pg_settings.postgres_user,
        password=pg_settings.postgres_password,
        host=pg_settings.postgres_host,
        port=pg_settings.postgres_port,
        path=f"/{pg_settings.postgres_db}"
    )

    redis_host: str
    redis_port: int

    cd_app_name: str
    cd_host: str
    cd_port: str
    logging_level: str

    csv_file_path: str


settings = Settings()
templates = Jinja2Templates(directory="src/templates")
