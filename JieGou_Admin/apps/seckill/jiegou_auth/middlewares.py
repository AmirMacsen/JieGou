from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions
import jwt
from django.conf import settings
from django.http.response import JsonResponse
from rest_framework.status import HTTP_403_FORBIDDEN
from jwt.exceptions import ExpiredSignatureError


class LoginCheckMiddleware(MiddlewareMixin):
    keyword = "Bearer"

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            auth = get_authorization_header(request).split()
            print("auth: {}".format(auth))

            if not auth or auth[0].lower() != self.keyword.lower().encode():
                raise exceptions.ValidationError("请传入JWT！")

            if len(auth) == 1:
                msg = "不可用的JWT请求头！"
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = '不可用的JWT请求头！JWT Token中间不应该有空格！'
                raise exceptions.AuthenticationFailed(msg)

            try:
                jwt_token = auth[1]
                jwt_info = jwt.decode(jwt_token, settings.JWT_SECRET_KEY, algorithms='HS256')
                userid = jwt_info.get('iss')
                setattr(request,'userid', userid)
            except ExpiredSignatureError:
                msg = "JWT Token已过期！"
                raise exceptions.AuthenticationFailed(msg)
        except Exception as e:
            print(e)
            return JsonResponse(data={"detail": "请先登录！"}, status=HTTP_403_FORBIDDEN)