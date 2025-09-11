from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAddressRequest(_message.Message):
    __slots__ = ("user_id", "realname", "mobile", "region", "detail")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    REALNAME_FIELD_NUMBER: _ClassVar[int]
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    realname: str
    mobile: str
    region: str
    detail: str
    def __init__(self, user_id: _Optional[int] = ..., realname: _Optional[str] = ..., mobile: _Optional[str] = ..., region: _Optional[str] = ..., detail: _Optional[str] = ...) -> None: ...

class UpdateAddressRequest(_message.Message):
    __slots__ = ("id", "realname", "mobile", "region", "detail", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    REALNAME_FIELD_NUMBER: _ClassVar[int]
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    realname: str
    mobile: str
    region: str
    detail: str
    user_id: int
    def __init__(self, id: _Optional[str] = ..., realname: _Optional[str] = ..., mobile: _Optional[str] = ..., region: _Optional[str] = ..., detail: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class DeleteAddressRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: int
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class AddressIdRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: int
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class AddressListRequest(_message.Message):
    __slots__ = ("user_id", "page", "size")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    page: int
    size: int
    def __init__(self, user_id: _Optional[int] = ..., page: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...

class AddressInfo(_message.Message):
    __slots__ = ("id", "realname", "mobile", "region", "detail")
    ID_FIELD_NUMBER: _ClassVar[int]
    REALNAME_FIELD_NUMBER: _ClassVar[int]
    MOBILE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    id: str
    realname: str
    mobile: str
    region: str
    detail: str
    def __init__(self, id: _Optional[str] = ..., realname: _Optional[str] = ..., mobile: _Optional[str] = ..., region: _Optional[str] = ..., detail: _Optional[str] = ...) -> None: ...

class AddressResponse(_message.Message):
    __slots__ = ("address",)
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: AddressInfo
    def __init__(self, address: _Optional[_Union[AddressInfo, _Mapping]] = ...) -> None: ...

class AddressListResponse(_message.Message):
    __slots__ = ("addresses",)
    ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    addresses: _containers.RepeatedCompositeFieldContainer[AddressInfo]
    def __init__(self, addresses: _Optional[_Iterable[_Union[AddressInfo, _Mapping]]] = ...) -> None: ...
