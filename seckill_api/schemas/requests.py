from pydantic import BaseModel, ConfigDict


class BuySchema(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    seckill_id:str
    count: int
    address: str