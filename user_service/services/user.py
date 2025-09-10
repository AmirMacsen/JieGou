import grpc
import sqlalchemy.exc
from google.protobuf import empty_pb2
from sqlalchemy import select
from sqlalchemy.sql.expression import update

from models.user import User
from protos import user_pb2,user_pb2_grpc
from utils.pwdutill import hash_password, verify_password


class UserService(user_pb2_grpc.UserServiceServicer):
    async def CreateUser(self, request:user_pb2.CreateUserRequest, context, session):
        mobile = request.mobile
        try:
            async with session.begin():
                user = User(mobile=mobile)
                session.add(user)
            response = user_pb2.UserInfoResponse(
                user_info=user.to_dict()
            )
            return response
        except sqlalchemy.exc.IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(f"用户{mobile}已存在")


    async def GetUserById(self, request:user_pb2.UserIdRequest, context, session):
        user_id = request.id
        try:
            async with session.begin():
                smt = select(User).where(User.id == user_id)
                query = await session.execute(smt)
                user = query.scalars().first()
                if not user:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"用户{user_id}不存在")
                response = user_pb2.UserInfoResponse(
                    user_info=user.to_dict()
                )
                return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务器异常")


    async def GetUserByMobile(self, request, context, session):
        mobile = request.mobile
        try:
            async with session.begin():
                smt = select(User).where(User.mobile == mobile)
                query = await session.execute(smt)
                user = query.scalars().first()
                if not user:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"用户{mobile}不存在")
                response = user_pb2.UserInfoResponse(
                    user_info=user.to_dict()
                )
                return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("服务器异常")


    async def GetUserList(self, request, context, session):
        page = request.page
        size = request.size
        limit = size
        offset = (page - 1) * size
        async with session.begin():
            try:
                smt = select(User).limit(limit).offset(offset)
                query = await session.execute(smt)
                users = query.scalars().all()
                user_list = []
                for user in users:
                    user_list.append(user_pb2.UserInfo(
                        id=user.id,
                        username=user.username,
                        mobile=user.mobile,
                        avatar=user.avatar,
                        is_staff=user.is_staff,
                        is_activate=user.is_activate,
                        last_login=user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "",
                    ))
                response = user_pb2.UserListResponse()
                response.user_list.extend(user_list)
                return response
            except Exception as e:
                import traceback
                traceback.print_exc()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("查询用户信息失败")


    async def UpdateUserAvatar(self, request, context, session):
        async with session.begin():
            user_id = request.id
            avatar = request.avatar
            stmt = update(User).where(User.id == user_id).values(avatar=avatar)
            result = await session.execute(stmt)

        row_count = result.rowcount
        if row_count == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
        else:
            return empty_pb2.Empty()


    async def UpdateUsername(self, request, context, session):
        async with session.begin():
            user_id = request.id
            username = request.username
            stmt = update(User).where(User.id == user_id).values(username=user_id)
            result = await session.execute(stmt)

        row_count = result.rowcount
        if row_count == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
        else:
            return empty_pb2.Empty()


    async def UpdatePassword(self, request, context, session):
        async with session.begin():
            user_id = request.id
            password = request.password
            hash_pwd = hash_password(password)
            stmt = update(User).where(User.id == user_id).values(password=hash_pwd)
            result = await session.execute(stmt)

        row_count = result.rowcount
        if row_count == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
        else:
            return empty_pb2.Empty()

    async def VerifyUser(self, request, context, session):
        async with session.begin():
            mobile = request.mobile
            password = request.password

            stmt_q = select(User).where(User.mobile == mobile)
            query = await session.execute(stmt_q)
            user = query.scalars().first()

        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
        elif not verify_password(password, user.password):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("密码错误")

        response = user_pb2.UserInfoResponse(
            user_info=user.to_dict(),
        )
        return  response


    async def GetOrCreateUserByMobile(self, request, context, session):
        mobile = request.mobile
        async with session.begin():
            stmt_q = select(User).where(User.mobile == mobile)
            query = await session.execute(stmt_q)
            user = query.scalars().first()

            if not user:
                user = User(mobile=mobile)
                session.add(user)

        response = user_pb2.UserInfoResponse(
            user_info=user.to_dict(),
        )

        return response




