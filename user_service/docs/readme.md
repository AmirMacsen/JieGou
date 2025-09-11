python -m grpc_tools.protoc -I. --pyi_out=. --python_out=. --grpc_python_out=. temperature.proto


alembic revision --autogenerate -m "Added temperature table"
alembic upgrade head
