import uuid
from typing import List, Dict

import consul
from dns import asyncresolver, rdatatype
from loguru import logger

import settings
from utils.local_ip_port import get_one_local_ip_and_port
from utils.single import SingletonMeta

class ServiceAddress:
    def __init__(self, host:str, port:int):
        self.host = host
        self.port = port
        self.count = 0

    def increment(self):
        self.count += 1


class LoadBalancer:
    def __init__(self, addresses: List[Dict[str,str|int]]=None):
        self.addresses: List[ServiceAddress] = []

    def init_addresses(self, addresses: List[Dict[str,str|int]]):
        self.addresses.clear()
        for address in addresses:
            self.addresses.append(ServiceAddress(address.get("host"), address.get("port")))


    def get_address(self):
        if len(self.addresses):
            self.addresses.sort(key=lambda x: x.count)
            address = self.addresses[0]
            address.increment()
            return address.host, address.port
        return None



class SingletonConsul(metaclass=SingletonMeta):
    def __init__(self):
        self.consul_host = settings.CONSUL_HOST
        self.consul_port = settings.CONSUL_PORT
        self.client = consul.Consul(self.consul_host, self.consul_port)
        self.service_id = uuid.uuid4().hex
        self.host, _ = get_one_local_ip_and_port()
        self.port = settings.SERVER_PORT
        self.consul_dns_port = settings.CONSUL_DNS_PORT
        self.user_service_load_balancer = LoadBalancer()

    def register_consul(self):
        self.client.agent.service.register(
            name="user_api",
            service_id=self.service_id,
            address=self.host,
            port=self.port,
            tags=["user", "http"],
            check=consul.Check.http(url=f"http://{self.host}:{self.port}/health", interval="10s")
        )

    def deregister_consul(self):
        self.client.agent.service.deregister(self.service_id)

    async def fetch_user_service_addresses(self):
        resolver = asyncresolver.Resolver()
        resolver.nameservers = [self.consul_host]
        resolver.port = self.consul_dns_port
        anwser_ips = await resolver.resolve(f"user_service.service.consul", rdtype=rdatatype.A)
        ips = [ info.address for info in anwser_ips]
        answer_ports = await resolver.resolve(f"user_service.service.consul", rdtype=rdatatype.SRV)
        ports = [info.port for info in answer_ports]

        user_addresses = []
        for index, port in enumerate(ports):
            if len(ips) == 1:
                user_addresses.append({"host": ips[0], "port": port})
            else:
                user_addresses.append({"host": ips[index], "port": port})

        logger.info(f"获取到用户服务地址: {user_addresses}")
        self.user_service_load_balancer.init_addresses(user_addresses)

    def get_user_service_address(self):
        return self.user_service_load_balancer.get_address()