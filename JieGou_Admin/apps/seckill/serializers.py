from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer

from apps.seckill.models import Commodity, Seckill


class CommoditySerializer(ModelSerializer):
    """
    商品序列化器
    """
    class Meta:
        model = Commodity
        fields = '__all__'
        extra_kwargs = {
            "create_time": {"read_only": True},
            "id": {"read_only": True},
        }


class SeckillSerializer(ModelSerializer):
    commodity = CommoditySerializer(read_only=True)
    commodity_id = CharField(write_only=True)
    class Meta:
        model = Seckill
        exclude = ('version_id',)
        extra_kwargs = {
            "create_time": {"read_only": True},
            "id": {"read_only": True},
        }
