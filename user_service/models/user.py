import random
import string

from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy_serializer.serializer import SerializerMixin

from utils.snowflake.snowflake import generate_id
from . import Base

def generate_username():
    code = "".join(random.sample(string.digits, 6))
    return "JieGou%s" % code

class User(Base, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ("-password",)
    id = Column(BigInteger, primary_key=True, default=generate_id)
    mobile = Column(String(20), unique=True, index=True)
    username = Column(String(20),default=generate_username)
    password = Column(String(300), nullable=True)
    avatar = Column(String(200), nullable=True)
    is_activate = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    last_login = Column(DATETIME, nullable=True)
