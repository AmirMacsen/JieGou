import asyncio
import json

from kafka import KafkaConsumer
from loguru import logger

import settings
from models import AsyncSessionFactory
from models.order import Order
from utils.cache import jiegou_redis
from utils.jiegou_alipay import jiegou_alipay

async def seckill_queue_handler():
    consumer = KafkaConsumer(
        'seckills',
        bootstrap_servers=[settings.KAFKA_SERVER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None
    )
    for message in consumer:
        seckill_dict = message.value
        seckill_id = seckill_dict['seckill_id']
        user_id = seckill_dict['user_id']
        count = seckill_dict['count']
        address = seckill_dict['address']

        seckill = await jiegou_redis.get_seckill(seckill_id)
        if not seckill:
            logger.info(f'{seckill_id}秒杀商品不存在！')
        if count > seckill['sk_per_max_count']:
            logger.info(f"{user_id}抢购了{count}，超过了{seckill['sk_per_max_count']}")
        async with AsyncSessionFactory() as session:
            async with session.begin():
                order = Order(
                    user_id=user_id, seckill_id=seckill_id, count=count,
                    amount=seckill['sk_price'] * count,
                    address=address
                )
                session.add(order)
            await session.refresh(order, attribute_names=['seckill'])
        alipay_order = jiegou_alipay.app_pay(
            out_trade_no=str(order.id),
            total_amount=float(order.amount),
            subject=seckill['commodity']['title']
        )
        await jiegou_redis.add_order(order, alipay_order)


if __name__ == '__main__':
    asyncio.run(seckill_queue_handler())
