from pydantic import BaseModel


class LoginModel(BaseModel):
    mobile: str
    code: str

class UpdateUsernameModel(BaseModel):
    username: str


class UpdatePasswordModel(BaseModel):
    password: str

class UpdateAvatarModel(BaseModel):
    avatar: str


class CreateAddressModel(BaseModel):
    realname: str
    mobile: str
    region: str
    detail: str

class AddressModel(BaseModel):
    id: str
    realname: str
    mobile: str
    region: str
    detail: str

class DeleteAddressModel(BaseModel):
    id: str

class UpdateAddressModel(BaseModel):
    id: str
    realname: str
    mobile: str
    region: str
    detail: str

class LoginWithPwdModel(BaseModel):
    mobile: str
    password: str

