from loguru import logger
from unisdk.sms import UniSMS
from unisdk.exception import UniException

# 初始化
client = UniSMS("your access key id", "your access key secret") # 若使用简易验签模式仅传入第一个参数即可


async def send_sms(mobile: str, code: str):
    try:
      # 发送短信
      res = await client.send({
        "to": mobile,
        "signature": "UniSMS",
        "templateId": "login_tmpl",
        "templateData": {
          "code": code
        }
      })
      return res.data
    except UniException as e:
      logger.error(e)