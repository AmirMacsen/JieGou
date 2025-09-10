import grpc

from protos import user_pb2_grpc, user_pb2


def main():
    with grpc.insecure_channel('localhost:5001') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        request = user_pb2.CreateUserRequest(
            mobile="18888888994",
        )

        response = stub.CreateUser(request)
        print(response)


if __name__ == '__main__':
    main()