from functools import wraps

import grpc
from loguru import logger
from fastapi.exceptions import HTTPException

from utils.status_code import get_http_code


def grpc_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except grpc.RpcError as e:
            logger.error(e)
            raise HTTPException(status_code=get_http_code(e.code()), detail=e.details())
        except:
            logger.error("请求异常")
            return HTTPException(status_code=500, detail="服务器内部错误")
    return  wrapper