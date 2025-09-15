from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict


class ResultEnum(Enum):
    SUCCESS = 0
    FAIL = 1


class ResponseModel(BaseModel):
    result: ResultEnum = ResultEnum.SUCCESS


class CommoditySchema(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: str
    title: str
    price: float
    covers: List[str]
    detail: str
    create_time: datetime

class SeckillSchema(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: str
    sk_price: float
    start_time: datetime
    end_time: datetime
    create_time: datetime
    max_sk_count: int
    stock: int
    sk_per_max_count: int
    commodity: CommoditySchema

class SeckillListSchema(BaseModel):
    seckills: List[SeckillSchema]


class OrderSchema(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: str
    seckill_id: int
    amount: float
    count: int
    address: str
    status: int
    create_time: datetime
    seckill: SeckillSchema

class OrderListSchema(BaseModel):
    orders: List[OrderSchema]





