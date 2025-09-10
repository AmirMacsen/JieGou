import asyncio

import grpc.aio

from protos import user_pb2_grpc
from services.user import UserService
from services.interceptors import UserInterceptor

async def main():
    server = grpc.aio.server(interceptors=[UserInterceptor()])
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("0.0.0.0:5001")
    await server.start()
    print("user grpc service starting....")
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(main())