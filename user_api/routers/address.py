from fastapi import APIRouter, Depends

from schemas.request import CreateAddressModel, AddressModel, DeleteAddressModel, UpdateAddressModel
from schemas.response import ResponseModel
from services.address import AddressServiceClient
from utils.auth import AuthHandler

router = APIRouter(prefix="/address", tags=["address"])

auth_handler = AuthHandler()

address_service_client = AddressServiceClient()


@router.post("/add", response_model=AddressModel)
async def create_address(data: CreateAddressModel,
                         user_id: int = Depends(auth_handler.auth_access_dependency)):

    address = await address_service_client.create_address(user_id, data.realname,
                                          data.mobile, data.region, data.detail)

    return address

@router.delete("/delete", response_model=ResponseModel)
async def delete_address(data:DeleteAddressModel, user_id: int = Depends(auth_handler.auth_access_dependency)):
    await address_service_client.delete_address(data.id, user_id)
    return ResponseModel()


@router.put("/update", response_model=ResponseModel)
async def update_address(data: UpdateAddressModel,
                        user_id: int = Depends(auth_handler.auth_access_dependency)):
    await address_service_client.update_address(data.id, data.realname,
                                          data.mobile, data.region, data.detail, user_id)
    return ResponseModel()

@router.get("/detail/{id}", response_model=AddressModel)
async def get_address(id: str, user_id: int = Depends(auth_handler.auth_access_dependency)):
    address = await address_service_client.get_address_by_id(id, user_id)
    return address

@router.get("/list", response_model=list[AddressModel])
async def address_list(page:int=1, size:int=10, user_id: int = Depends(auth_handler.auth_access_dependency)):
    addresses = await address_service_client.get_address_list(user_id, page, size)
    return addresses


