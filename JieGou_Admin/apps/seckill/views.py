from datetime import datetime
import json

from rest_framework import viewsets
from django.core.cache import cache

from apps.seckill.serializers import CommoditySerializer, SeckillSerializer
from apps.seckill.models import Commodity, Seckill


class CommodityViewSet(viewsets.ModelViewSet):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer


class SeckillViewSet(viewsets.ModelViewSet):
    queryset = Seckill.objects.all()
    serializer_class = SeckillSerializer

    SECKILL_KEY = 'seckill_{}'

    def perform_create(self, serializer):
        # 执行父类的方法添加到数据库并保存到redis
        serializer.save()
        instance = serializer.instance

        ex = int((instance.end_time - datetime.now()).total_seconds())
        data = json.dumps(self.serializer_class(instance).data)
        key = self.SECKILL_KEY.format(instance.id)
        cache.set(key, data, timeout=ex)

    def retrieve(self, request, *args, **kwargs):
        # 1. 先从缓存中查找
        pk = kwargs['pk']
        key = self.SECKILL_KEY.format(seckill_id=pk)
        value = cache.get(key)
        if value:
            return value
        # 2. 再从数据库中查找
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        # 1. 更新数据库
        super().perform_update(serializer)
        # 2. 更新缓存
        instance = serializer.instance
        if instance.end_time > datetime.now():
            ex = int((instance.end_time - datetime.now()).total_seconds())
            data = json.dumps(self.serializer_class(instance).data)
            key = self.SECKILL_KEY.format(seckill_id=instance.id)
            cache.set(key, data, timeout=ex)

    def perform_destroy(self, instance):
        # 1. 从数据库中删除
        super().perform_destroy(instance)
        # 2. 从缓存中删除
        key = self.SECKILL_KEY.format(seckill_id=instance.id)
        cache.delete(key)






