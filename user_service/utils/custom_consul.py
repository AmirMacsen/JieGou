import uuid

import consul

import settings
from utils.single import SingletonMeta


class SingletonConsul(metaclass=SingletonMeta):
    def __init__(self):
        self.client = consul.Consul(host=settings.CONSUL_HOST, port=settings.CONSUL_PORT)
        self.service_id = uuid.uuid4().hex

    def register_consul(self, host, port):
        self.client.agent.service.register(
            name="user_service",
            service_id=self.service_id,
            address=host,
            port=port,
            tags=["user", "grpc"],
            check=consul.Check.tcp(host=host, port=port, interval="10s")
        )

    def deregister_consul(self):
        self.client.agent.service.deregister(self.service_id)