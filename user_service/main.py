import asyncio

import grpc.aio
from loguru import logger

from protos import user_pb2_grpc, address_pb2_grpc
from services.address import AddressService
from services.interceptors import UserInterceptor
from services.user import UserService
from utils.custom_consul import SingletonConsul
from utils.local_ip_port import get_one_local_ip_and_port

consul_client = SingletonConsul()

async def main():
    logger.add("logs/app.log", rotation="500 MB", enqueue=True, compression="zip")
    local_host, port = get_one_local_ip_and_port()
    server = grpc.aio.server(interceptors=[UserInterceptor()])
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    address_pb2_grpc.add_AddressServicer_to_server(AddressService(), server)
    server.add_insecure_port(f"{local_host}:{port}")
    # 向consul注册 这里不使用异步，是因为在服务启动之前开始
    consul_client.register_consul(local_host, port)
    await server.start()
    logger.info(f"user grpc service starting on {local_host}:{port}....")
    try:
        await server.wait_for_termination()
    except:
        pass
    consul_client.deregister_consul()


if __name__ == '__main__':
    asyncio.run(main())