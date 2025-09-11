import os.path
import uuid

import oss2
from asgiref.sync import sync_to_async
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi import UploadFile
from loguru import logger


async def oss_upload_image(file:UploadFile, max_size=1024*1024) ->str|None:
    if file.size > max_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片大小不能超过1M")
    extension = os.path.splitext(file.filename)[1]
    if extension not in [".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片格式错误")

    access_key_id = os.getenv("ALIYUN_ACCESS_KEY")
    access_key_secret = os.getenv("ALIYUN_ACCESS_TOKEN")
    endpoint = os.getenv("ALIYUN_ENDPOINT")
    bucket = os.getenv("ALIYUN_BUCKET")
    region = os.getenv("ALIYUN_REGION")
    oss_domain = os.getenv("ALIYUN_OSS_DOMAIN")

    auth = oss2.AuthV4(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint=endpoint, bucket_name=bucket, region=region)

    file_name = f"{uuid.uuid4().hex}{extension}"
    file_data = await file.read()
    put_object = sync_to_async(bucket.put_object)
    result = await put_object(key=file_name, data=file_data)
    if result.status == 200:
        file_url = f"{oss_domain}{file_name}"
        return file_url
    else:
        logger.error(result.resp.text)
        return None



