import random
import string

from fastapi import APIRouter, HTTPException, Depends, UploadFile
from loguru import logger

from schemas.request import LoginModel, UpdateUsernameModel, UpdatePasswordModel, UpdateAvatarModel, LoginWithPwdModel
from schemas.response import ResponseModel, LoginResponseModel, UserModel, UpdatedAvatarModel
from services.user import UserServiceClient
from utils.auth import AuthHandler
from utils.cache import TllRedis

router = APIRouter(prefix="/user", tags=["user"])

auth_handler = AuthHandler()
user_service_client = UserServiceClient()

@router.get("/smscode/{mobile}", response_model=ResponseModel)
async def get_smscode(mobile: str):
    code = "".join(random.sample(string.digits, 4))
    await TllRedis().set_sms_code(mobile, code)
    logger.info(f"mobile: {mobile}, code: {code}")
    return ResponseModel()


@router.post("/login", response_model=LoginResponseModel)
async def login(data: LoginModel):
    mobile = data.mobile
    code = data.code

    cache_code = await TllRedis().get_sms_code(mobile)
    if cache_code is None:
        raise HTTPException(status_code=400, detail="验证码已经过期")

    if cache_code != code:
        raise HTTPException(status_code=500, detail="验证码错误")
    else:
        user = await user_service_client.get_or_create_user_by_mobile(mobile)
        tokens = auth_handler.encode_login_token(user.id)
        # 单点登录 1. 删除刷新令牌 2.存储最新的刷新令牌
        await TllRedis().delete_refresh_token(user.id)
        await TllRedis().set_refresh_token(user.id, tokens["refresh_token"])
        return {
            "user": user,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"]
        }

@router.get("/refresh/token")
async def refresh_token(user_id: int = Depends(auth_handler.auth_refresh_dependency)):
    access_token = auth_handler.encode_update_token(user_id)
    return access_token


@router.put("/update/username", response_model=ResponseModel)
async def update_username(data: UpdateUsernameModel, user_id: int = Depends(auth_handler.auth_access_dependency)):
    await user_service_client.update_username(user_id,username=data.username)
    return ResponseModel()


@router.put("/update/password", response_model=ResponseModel)
async def update_password(data: UpdatePasswordModel, user_id: int = Depends(auth_handler.auth_access_dependency)):
    await user_service_client.update_password(user_id,password=data.password)
    return ResponseModel()


@router.post("/update/avatar", response_model=UpdatedAvatarModel)
async def update_avatar(file: UploadFile, user_id: int = Depends(auth_handler.auth_access_dependency)):
    from utils.alyoss import oss_upload_image
    file_url = await oss_upload_image(file)
    if file_url is None:
        raise HTTPException(status_code=500, detail="上传图片失败")
    await user_service_client.update_avatar(user_id,avatar=file_url)
    return UpdatedAvatarModel(avatar=file_url)


@router.get("/mine", response_model=UserModel)
async def get_mine_info(user_id: int = Depends(auth_handler.auth_access_dependency)):
    user = await user_service_client.get_user_by_id(user_id)
    return user


@router.post("/logout", response_model=ResponseModel)
async def logout(user_id: int = Depends(auth_handler.auth_access_dependency)):
    await TllRedis().delete_refresh_token(user_id)
    return ResponseModel()

@router.post("/login/with/pwd", response_model=LoginResponseModel)
async def login_with_pwd(data:LoginWithPwdModel):
    mobile = data.mobile
    password = data.password

    # 验证用户账号密码是否正确
    user = await user_service_client.verify_user(mobile,password)
    if user is None:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    tokens = auth_handler.encode_login_token(user.id)
    await TllRedis().set_refresh_token(user.id, tokens["refresh_token"])
    return {
        "user": user,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    }

