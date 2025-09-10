from typing import Any,Callable

import grpc
from grpc_interceptor.exceptions import GrpcException
from grpc_interceptor.server import AsyncServerInterceptor

from models import AsyncSessionFactory

class UserInterceptor(AsyncServerInterceptor):
    async def intercept(
            self,
            method: Callable,
            request_or_iterator: Any,
            context: grpc.ServicerContext,
            method_name: str,
    ) -> Any:
        try:
            session = AsyncSessionFactory()
            response = await method(request_or_iterator, context, session)
            return response
        except GrpcException as e:
            await context.set_code(e.status_code)
            await context.set_details(e.details)
            raise
        finally:
            await session.close()