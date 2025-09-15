from pathlib import Path

from .single import SingletonMeta
from alipay import AliPay, AliPayConfig
import settings


class JieGouAlipay(metaclass=SingletonMeta):
    def __init__(self):
        project_root = Path(__file__).parent.parent.absolute()

        # 构建密钥文件的完整路径
        app_private_key_path = project_root / 'keys' / 'app_private.key'
        app_public_key_path = project_root / 'keys' / 'alipay_public.pem'

        with open(app_private_key_path, mode='r') as f:
            app_private_key_string = f.read()
        with open(app_public_key_path, mode='r') as f:
            alipay_public_key_string = f.read()

        client = AliPay(
            appid=settings.ALIPAY_APP_ID,
            # app_notify_url="http://www.example.com/notify",  # 默认回调 url
            app_notify_url="http://189gw1wl5762.vicp.fun/seckill/alipay/notify",
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            # 沙箱环境需要设置debug=True
            debug=True,  # 默认 False
            verbose=True,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )
        self.client = client

    def app_pay(self, out_trade_no: str, total_amount: float, subject: str):
        order_string = self.client.api_alipay_trade_app_pay(
            out_trade_no=out_trade_no,
            total_amount=total_amount,
            subject=subject
        )
        return order_string


jiegou_alipay = JieGouAlipay()