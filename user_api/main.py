from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

import settings
from hooks.lifespan import lifespan
from hooks.middlewares import log_middleware
from routers import user, address

app = FastAPI(
    lifespan=lifespan
)

app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

app.include_router(user.router)
app.include_router(address.router)

@app.get('/health')
async def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    load_dotenv()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVER_PORT)
