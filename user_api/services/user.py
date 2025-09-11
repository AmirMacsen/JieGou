import grpc.aio

from protos import user_pb2_grpc, user_pb2
from services.decorators import grpc_error_handler
from utils.single import SingletonMeta

class UserStub:
    def __init__(self):
        self.user_service_addr = "localhost:5001"


    async def __aenter__(self):
        self.channel = grpc.aio.insecure_channel(self.user_service_addr)
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