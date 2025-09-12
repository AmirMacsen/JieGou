import os.path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from utils.cache import TllRedis


from utils.custom_consul import SingletonConsul

consul_client = SingletonConsul()


@asynccontextmanager
async def lifespan(app:FastAPI):
    if not os.path.exists("logs"):
        os.mkdir("logs")
    logger.add("logs/app.log", rotation="500 MB", enqueue=True, compression="zip")
    # 向consul注册
    consul_client.register_consul()
    await consul_client.fetch_user_service_addresses()
    yield
    await TllRedis().close()
    consul_client.deregister_consul()