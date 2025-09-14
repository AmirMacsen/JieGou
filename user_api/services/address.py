import grpc
from fastapi import HTTPException

from protos import address_pb2_grpc, address_pb2
from services.decorators import grpc_error_handler
from utils.custom_consul import SingletonConsul
from utils.single import SingletonMeta

jiegou_consul = SingletonConsul()

class AddressStub:
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
            stub = address_pb2_grpc.AddressStub(self.channel)
            return stub

    async def __aexit__(self, exc_type, exc, tb):
        await self.channel.close()


class AddressServiceClient(metaclass=SingletonMeta):

    @grpc_error_handler
    async def create_address(self, user_id:int, realname:str, mobile:str, region:str, detail:str):
        async with AddressStub() as stub:
            request = address_pb2.CreateAddressRequest(user_id=user_id, realname=realname,
                                                       mobile=mobile, region=region, detail=detail)
            response = await stub.CreateAddress(request)
            return response.address

    @grpc_error_handler
    async def update_address(self, id:str, realname:str, mobile:str, region:str, detail:str, user_id:int):
        async with AddressStub() as stub:
            request = address_pb2.UpdateAddressRequest(
                id=id,
                realname=realname,
                mobile=mobile,
                region=region,
                detail=detail,
                user_id=user_id
            )
            await stub.UpdateAddress(request)

    @grpc_error_handler
    async def delete_address(self, id:str, user_id:int):
        async with AddressStub() as stub:
            request = address_pb2.DeleteAddressRequest(id=id, user_id=user_id)
            await stub.DeleteAddress(request)


    @grpc_error_handler
    async def get_address_by_id(self, id:str, user_id:int):
        async with AddressStub() as stub:
            request = address_pb2.AddressIdRequest(id=id, user_id=user_id)
            response = await stub.GetAddressById(request)
            return response.address


    @grpc_error_handler
    async def get_address_list(self, user_id:int, page:int, size:int):
        async with AddressStub() as stub:
            request = address_pb2.AddressListRequest(user_id=user_id, page=page, size=size)
            response = await stub.GetAddressList(request)
            return response.addresses


