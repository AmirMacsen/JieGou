import redis.asyncio as redis
from .single import SingletonMeta

class TllRedis(metaclass=SingletonMeta):
    SMS_CODE_PREFIX = "sms_code_"
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=0)

    async def set(self, key, value, ex=5*60*60):
        await self.client.set(key, value, ex)


    async def get(self,  key):
        value = await self.client.get(key)
        if type(value) == bytes:
            return value.decode("utf-8")
        else:
            return value


    async def set_sms_code(self, mobile, code):
        await self.set(f"{self.SMS_CODE_PREFIX}{mobile}", code)

    async def get_sms_code(self, mobile):
        return await self.get(f"{self.SMS_CODE_PREFIX}{mobile}")
    async def close(self):
        await self.client.aclose()

