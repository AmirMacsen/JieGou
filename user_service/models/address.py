import uuid

from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from . import Base

def generate_id():
    return uuid.uuid4().hex

class Address(Base, SerializerMixin):
    __tablename__ = 'address'
    serialize_only = ("id", "realname", "mobile", "region", "detail")
    id = Column(String(200), primary_key=True, default=generate_id)
    realname = Column(String(200))
    mobile = Column(String(20))
    region = Column(String(200))
    detail = Column(String(500))

    user_id = Column(BigInteger, ForeignKey('users.id'))
    user = relationship("User", backref="addresses")