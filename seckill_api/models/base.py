from sqlalchemy import Column, BigInteger

import settings
from utils.snowflake.snowflake import Snowflake

id_worker = Snowflake(
    datacenter_id=settings.DATACENTER_ID,
    worker_id=settings.WORKER_ID,
    sequence=0
)


def generate_id():
    return id_worker.get_id()


class SnowFlakeIdModel:
    id = Column(BigInteger, primary_key=True, default=generate_id)