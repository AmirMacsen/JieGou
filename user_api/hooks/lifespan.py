import os.path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from utils.cache import TllRedis


@asynccontextmanager
async def lifespan(app:FastAPI):
    if not os.path.exists("logs"):
        os.mkdir("logs")
    logger.add("logs/app.log", rotation="500 MB", enqueue=True, compression="zip")
    yield
    await TllRedis().close()