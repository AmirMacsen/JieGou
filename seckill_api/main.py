from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

import settings
from hooks.middlewares import db_session_middleware
from routers import seckill, order

app = FastAPI()

app.add_middleware(BaseHTTPMiddleware, dispatch=db_session_middleware)
app.include_router(seckill.router)
app.include_router(order.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVER_PORT)