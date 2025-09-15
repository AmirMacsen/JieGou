import datetime
import json

from fastapi import APIRouter, HTTPException, Depends
from fastapi.requests import Request
from sqlalchemy import select
from starlette import status
from kafka import KafkaProducer

from hooks.dependes import get_db_session
from models import AsyncSessionFactory
from models.order import Order, OrderStatusEnum
from models.seckill import Seckill
from schemas.requests import BuySchema
from schemas.response import SeckillListSchema, SeckillSchema, ResponseModel
from utils.auth import AuthHandler
from utils.cache import jiegou_redis
from utils.jiegou_alipay import jiegou_alipay
import settings

router = APIRouter(
    prefix="/seckill",
    tags=["seckill"],
)

auth_handler = AuthHandler()

kafka_producer = KafkaProducer(bootstrap_servers=settings.KAFKA_SERVER,
                               value_serializer=lambda x: json.dumps(x).encode('utf-8'))

@router.get("/ing", response_model=SeckillListSchema)
async def get_seckill_ing(request: Request, page: int = 1, size: int = 10):
    async with request.state.session.begin():
        start_time = datetime.datetime.now()
        offset = (page - 1) * size
        stmt = select(Seckill).where(Seckill.start_time < start_time,
                                     Seckill.end_time > start_time).offset(offset) \
            .limit(size).order_by(Seckill.start_time.desc())
        query = await request.state.session.execute(stmt)
        rows = query.scalars()
    return {"seckills": rows}


@router.get("/will", response_model=SeckillListSchema)
async def get_seckill_will(request: Request, page: int = 1, size: int = 10):
    async with request.state.session.begin():
        start_time = datetime.datetime.now()
        offset = (page - 1) * size
        stmt = select(Seckill).where(Seckill.start_time >start_time).offset(offset) \
            .limit(size).order_by(Seckill.start_time.desc())
        query = await request.state.session.execute(stmt)
        rows = query.scalars()
    return {"seckills": rows}

@router.put("/lock/{seckill_id}")
async def lock_seckill(seckill_id:int, session:AsyncSessionFactory=Depends(get_db_session)):
    """
    悲观锁的实现 利用mysql 的for update 行级锁
    :param request:
    :return:
    """
    async with session.begin():
        # 默认是写锁， 如果 with_for_update(read=True)，就是读锁，写锁就是不让读和写，读锁就是只读
        stmt = select(Seckill).where(Seckill.id==seckill_id).with_for_update()
        query = await session.execute(stmt)
        row = query.scalars().first()
        row.stock -= 1
    return {"message": "ok"}


@router.put("/lock_positive/{seckill_id}")
async def lock_seckill(seckill_id:int, session:AsyncSessionFactory=Depends(get_db_session)):
    """
    乐观锁的实现 通过模型的记录的version_id字段，实现并发控制，也就是在数据库表中添加column实现

    不管是悲观锁还是乐观锁都需要select
    :param request:
    :return:
    """
    async with session.begin():
        stmt = select(Seckill).where(Seckill.id==seckill_id)
        query = await session.execute(stmt)
        row = query.scalar()
        row.stock -= 1
    return {"message": "ok"}

# @router.post("/buy")
# async def buy_seckill(data:BuySchema, session:AsyncSessionFactory=Depends(get_db_session),
#                       user_id:int=Depends(auth_handler.auth_access_dependency)):
#     """
#     秒杀下单
#     :param session:
#     :param user_id:
#     :return:
#     """
#     seckill_id = data.seckill_id
#     count = data.count
#     address = data.address
#     # 用户只能抢购一次
#     async with session.begin():
#         stmt = select(Order).where(Order.user_id==user_id, Order.seckill_id==seckill_id)
#         query = await session.execute(stmt)
#         row = query.scalars().first()
#         if row:
#             raise HTTPException(status_code=400, detail="用户只能抢购一次")
#
#         # 使用悲观锁，虽然影响性能，但是有队列兜底，因此影响不大
#         stmt = select(Seckill).where(Seckill.id==seckill_id).with_for_update()
#         query = await session.execute(stmt)
#         row_seckill = query.scalars().first()
#         if not row_seckill:
#             raise HTTPException(status_code=400, detail=f"该秒杀不存在")
#
#         if row_seckill.stock < count:
#             raise HTTPException(status_code=400, detail="库存不足")
#
#         if row_seckill.sk_per_max_count < count:
#             raise HTTPException(status_code=400, detail="超出最大秒杀数量")
#         row_seckill.stock -= count
#
#
#     # 开启订单生成的事务
#     async with session.begin():
#         order = Order(user_id=user_id, seckill_id=seckill_id, amount=row_seckill.sk_price * count,
#                     count=count, address=address, status=OrderStatusEnum.UNPAYED)
#
#         session.add(order)
#
#
#     # 支付订单的生成
#     order_string = jiegou_alipay.app_pay(out_trade_no=str(order.id),
#                                          total_amount=float(order.amount),
#                                          subject=row_seckill.commodity.title)
#     return {"alipay_order": order_string}

@router.post("/buy", response_model=ResponseModel)
async def buy_seckill(data:BuySchema, session:AsyncSessionFactory=Depends(get_db_session),
                      user_id:int=Depends(auth_handler.auth_access_dependency)):
    """
    秒杀下单
    :param session:
    :param user_id:
    :return:
    """
    # 判断是否已经存在订单
    order = await jiegou_redis.get_order(user_id, data.seckill_id)
    if order:
        if order['status'] == OrderStatusEnum.UNPAYED.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='您有尚未支付的订单！')
        if order['status'] == OrderStatusEnum.PAYED.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='您已经抢购过商品！')

    # 从redis中扣减库存
    result = await jiegou_redis.decrease_stock(seckill_id=int(data.seckill_id))
    if not result:
        raise HTTPException(status_code=400, detail="库存不足")
    form_data = data.model_dump()
    form_data['user_id'] = user_id
    kafka_producer.send('seckills', form_data)
    return ResponseModel()


@router.get("/detail/{seckill_id}", response_model=SeckillSchema)
async def seckill_detail(seckill_id: int, session: AsyncSessionFactory=Depends(get_db_session)):
    async with session.begin():
        result = await session.execute(select(Seckill).where(Seckill.id==seckill_id))
        seckill = result.scalar()
        if not seckill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='该秒杀不存在！')
        return seckill

@router.post("/alipay/notify")
async def notify(request: Request, session: AsyncSessionFactory=Depends(get_db_session)):
    form_data = await request.form()
    data = dict(form_data)
    sign = data.pop("sign")
    result = jiegou_alipay.client.verify(data, sign)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='该请求无效！')
    # 自己的订单号
    out_trade_no = data.get('out_trade_no')
    # 支付宝的订单号
    trade_no = data.get('trade_no')
    trade_status = data.get('trade_status')
    async with session.begin():
        result = await session.execute(select(Order).where(Order.id == out_trade_no))
        order = result.scalar()
        if not order:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='该订单不存在！')
        order.alipay_trade_no = trade_no
        if trade_status == 'WAIT_BUYER_PAY':
            order.status = OrderStatusEnum.UNPAYED
        elif trade_status == 'TRADE_CLOSED':
            order.status = OrderStatusEnum.REFUNDED
        elif trade_status == 'TRADE_SUCCESS':
            order.status = OrderStatusEnum.PAYED
        elif trade_status == 'TRADE_FINISHED':
            order.status = OrderStatusEnum.FINISHED

    jiegou_redis.add_order(order, alipay_order=None)

    return "success"


@router.get('/order/{seckill_id}')
async def get_seckill_order(
    seckill_id: int,
    user_id: int=Depends(auth_handler.auth_access_dependency)
):
    order = await jiegou_redis.get_order(user_id, seckill_id)
    if not order:
        return {"alipay_order": ''}
    return {"alipay_order": order['alipay_order']}

