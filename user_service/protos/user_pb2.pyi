from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateUserRequest(_message.Message):
    __slots__ = ("mobile",)
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    mobile: str
    def __init__(self, mobile: _Optional[str] = ...) -> None: ...

class UserIdRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class UserMobileRequest(_message.Message):
    __slots__ = ("mobile",)
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    mobile: str
    def __init__(self, mobile: _Optional[str] = ...) -> None: ...

class UserUpdateAvatarRequest(_message.Message):
    __slots__ = ("id", "avatar")
    ID_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    id: int
    avatar: str
    def __init__(self, id: _Optional[int] = ..., avatar: _Optional[str] = ...) -> None: ...

class UserUpdatePasswordRequest(_message.Message):
    __slots__ = ("id", "password")
    ID_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    id: int
    password: str
    def __init__(self, id: _Optional[int] = ..., password: _Optional[str] = ...) -> None: ...

class UserUpdateUsernameRequest(_message.Message):
    __slots__ = ("id", "username")
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    def __init__(self, id: _Optional[int] = ..., username: _Optional[str] = ...) -> None: ...

class PageRequest(_message.Message):
    __slots__ = ("page", "size")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    page: int
    size: int
    def __init__(self, page: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...

class VerifyUserRequest(_message.Message):
    __slots__ = ("mobile", "password")
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    mobile: str
    password: str
    def __init__(self, mobile: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class UserInfo(_message.Message):
    __slots__ = ("id", "username", "mobile", "avatar", "is_activate", "is_staff", "last_login")
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    AVATAR_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVATE_FIELD_NUMBER: _ClassVar[int]
    IS_STAFF_FIELD_NUMBER: _ClassVar[int]
    LAST_LOGIN_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    mobile: str
    avatar: str
    is_activate: bool
    is_staff: bool
    last_login: str
    def __init__(self, id: _Optional[int] = ..., username: _Optional[str] = ..., mobile: _Optional[str] = ..., avatar: _Optional[str] = ..., is_activate: bool = ..., is_staff: bool = ..., last_login: _Optional[str] = ...) -> None: ...

class UserInfoResponse(_message.Message):
    __slots__ = ("user_info",)
    USER_INFO_FIELD_NUMBER: _ClassVar[int]
    user_info: UserInfo
    def __init__(self, user_info: _Optional[_Union[UserInfo, _Mapping]] = ...) -> None: ...

class UserListResponse(_message.Message):
    __slots__ = ("user_list",)
    USER_LIST_FIELD_NUMBER: _ClassVar[int]
    user_list: _containers.RepeatedCompositeFieldContainer[UserInfo]
    def __init__(self, user_list: _Optional[_Iterable[_Union[UserInfo, _Mapping]]] = ...) -> None: ...
