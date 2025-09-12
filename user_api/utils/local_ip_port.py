import socket
import errno
from typing import Tuple, Optional


def get_one_local_ip_and_port(start_port: int = 1024) -> Optional[Tuple[str, int]]:
    def _get_local_ip() -> str:
        """优先获取局域网IP，失败则退回127.0.0.1"""
        try:
            # 方法1：尝试用 UDP 套接字连接外部，获取系统选定的本地IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # 不会真的发包，只是用来获得本地出口IP
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            pass

        try:
            # 方法2：尝试通过主机名解析
            for addr_info in socket.getaddrinfo(socket.gethostname(), None):
                ip = addr_info[4][0]
                if not ip.startswith("127."):  # 排除环回
                    return ip
        except Exception:
            pass

        # 方法3：兜底 -> 回环地址
        return "127.0.0.1"

    local_ip = _get_local_ip()

    # 第二步：找第一个可用端口
    current_port = max(start_port, 65534)
    max_attempts = 1000
    attempts = 0

    while current_port <= 65535 and attempts < max_attempts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((local_ip, current_port))
                return (local_ip, current_port)
        except socket.error as e:
            if e.errno != errno.EADDRINUSE:
                # 只要不是端口占用，说明IP可能有问题，换成127.0.0.1重试
                if local_ip != "127.0.0.1":
                    local_ip = "127.0.0.1"
                    continue
                return None
        current_port -= 1
        attempts += 1

    return None
