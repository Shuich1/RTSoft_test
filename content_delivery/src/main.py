import logging

import aioredis
import uvicorn
from api.v1 import images
from core.config import settings
from core.logger import LOGGING
from db import cache, database
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from utils.fill_database import fill_database_from_csv

app = FastAPI(
    title="API для получения изображений по категориям",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse
)


@app.on_event("startup")
async def startup():
    database.data_storage = database.SQLAlchemyDataStorage()
    database.data_storage.connect(settings.db)
    database.data_storage.db_init()
    fill_database_from_csv(database.data_storage, settings.csv_file_path)
    cache.cache = cache.RedisCache(
        redis=await aioredis.create_redis_pool(
            (settings.redis_host, settings.redis_port),
            db=0,
            minsize=10,
            maxsize=20
        )
    )


@app.on_event("shutdown")
async def shutdown():
    database.data_storage.disconnect()
    await cache.cache.close()


app.include_router(
    images.router,
    prefix="/api/v1/images",
    tags=["images"]
)

if __name__ == '__main__':
    uvicorn.run(
        app=settings.cd_app_name,
        host=settings.cd_host,
        port=int(settings.cd_port),
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )
