from rest_framework.routers import DefaultRouter

from apps.seckill.views import CommodityViewSet, SeckillViewSet

app_name = 'seckill'

commodity_router =  DefaultRouter()
commodity_router.register('commodity', CommodityViewSet, basename='commodity')

seckill_router = DefaultRouter()
seckill_router.register('seckill', SeckillViewSet, basename='seckill')

urlpatterns = [] + commodity_router.urls  + seckill_router.urls