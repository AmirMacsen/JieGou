from models import AsyncSessionFactory
from fastapi.requests import Request


async def db_session_middleware(request:Request, call_next):
    session = AsyncSessionFactory()
    setattr(request.state, "session", session)
    response = await call_next(request)
    await session.close()
    return response