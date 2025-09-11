from enum import Enum

from pydantic import BaseModel


class ResultEnum(Enum):
    SUCCESS = 0
    FAIL = 1


class ResponseModel(BaseModel):
    result: ResultEnum = ResultEnum.SUCCESS


class UserModel(BaseModel):
    id: int
    mobile: str
    username: str
    avatar: str
    is_activate: bool
    is_staff: bool


class LoginResponseModel(BaseModel):
    user: UserModel
    access_token: str
    refresh_token: str


class UpdatedAvatarModel(BaseModel):
    avatar: str