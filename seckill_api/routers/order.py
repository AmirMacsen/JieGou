from fastapi import APIRouter, Depends
from sqlalchemy import select

from hooks.dependes import get_db_session
from models import AsyncSessionFactory
from models.order import Order
from schemas.response import OrderListSchema
from utils.auth import AuthHandler

router = APIRouter(
    prefix="/order",
    tags=["order"]
)

auth_handler = AuthHandler()

@router.get("/list", response_model=OrderListSchema)
async def get_order_list(page:int=1, size:int=10, session:AsyncSessionFactory=Depends(get_db_session),
                         user_id:int=Depends(auth_handler.auth_access_dependency)):
    """
    获取用户订单列表
    """
    offset = (page-1)*size
    async with session.begin():
        stmt = select(Order).where(Order.user_id==user_id).limit(size).offset(offset).order_by(Order.create_time.desc())
        query = await session.execute(stmt)
        rows = query.scalars().all()
        return {"orders": rows}

