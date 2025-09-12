import grpc.aio
from fastapi import HTTPException

from protos import user_pb2_grpc, user_pb2
from services.decorators import grpc_error_handler
from utils.custom_consul import SingletonConsul
from utils.single import SingletonMeta


jiegou_consul = SingletonConsul()

class UserStub:
    @property
    def user_service_address(self):
        data = jiegou_consul.get_user_service_address()
        if data:
            host, port = data
            return f"{host}:{port}"
        else:
            raise HTTPException(status_code=500, detail="用户服务未找到")

    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(self.user_service_address)
        stub = user_pb2_grpc.UserServiceStub(self.channel)
        return stub

    async def __aexit__(self, exc_type, exc, tb):
        await self.channel.close()


class UserServiceClient(metaclass=SingletonMeta):
    @grpc_error_handler
    async def get_or_create_user_by_mobile(self, mobile:str):
        async with UserStub() as stub:
            request = user_pb2.UserMobileRequest(mobile=mobile)
            response = await stub.GetOrCreateUserByMobile(request)
            return response.user_info

    @grpc_error_handler
    async def update_username(self, user_id:int, username:str):
        async with UserStub() as stub:
            request = user_pb2.UserUpdateUsernameRequest(id=user_id, username=username)
            await stub.UpdateUsername(request)

    @grpc_error_handler
    async def update_password(self, user_id:int, password:str):
        async with UserStub() as stub:
            request = user_pb2.UserUpdatePasswordRequest(id=user_id, password=password)
            await stub.UpdatePassword(request)

    @grpc_error_handler
    async def update_avatar(self, user_id:int, avatar:str):
        async with UserStub() as stub:
            request = user_pb2.UserUpdateAvatarRequest(id=user_id, avatar=avatar)
            await stub.UpdateUserAvatar(request)

    @grpc_error_handler
    async def get_user_by_id(self, user_id:int):
       async with UserStub() as stub:
           request = user_pb2.UserIdRequest(id=user_id)
           response = await stub.GetUserById(request)
           return response.user_info

    @grpc_error_handler
    async def get_user_by_mobile(self, mobile: str):
        async with UserStub() as stub:
            request = user_pb2.UserMobileRequest(mobile=mobile)
            response = await stub.GetUserByMobile(request)
            return response.user_info

    @grpc_error_handler
    async def get_user_list(self, page:int, size:int):
        async with UserStub() as stub:
            request = user_pb2.PageRequest(page=page, size=size)
            response = await stub.GetUserList(request)
            return response.user_list

    @grpc_error_handler
    async def verify_user(self, mobile:str, password:str):
        async with UserStub() as stub:
            request = user_pb2.VerifyUserRequest(mobile=mobile, password=password)
            response = await stub.VerifyUser(request)
            return response.user_info