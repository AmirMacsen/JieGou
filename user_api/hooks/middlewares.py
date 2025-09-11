from fastapi.requests import Request
from loguru import logger
from fastapi.responses import JSONResponse


async def log_middleware(request: Request, call_next):
    """
    日志中间件
    :param request:
    :param call_next:
    :return:
    """

    try:
        response = await call_next(request)
        await logger.complete()
        return response
    except Exception as e:
        logger.exception(f"请求异常: {e}")
        return JSONResponse(status_code=500, content={"detail": "服务器内部错误"})
