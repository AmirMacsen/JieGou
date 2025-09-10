import time
import threading

import settings


class Snowflake:
    def __init__(self, datacenter_id=1, worker_id=1, sequence=0):
        """
        初始化雪花算法

        :param datacenter_id: 数据中心ID (0-31)
        :param worker_id: 工作机器ID (0-31)
        :param sequence: 序列号 (0-4095)
        """
        # 时间戳位数 (41位)
        self.timestamp_bits = 41
        # 数据中心ID位数 (5位)
        self.datacenter_id_bits = 5
        # 工作机器ID位数 (5位)
        self.worker_id_bits = 5
        # 序列号位数 (12位)
        self.sequence_bits = 12

        # 最大值计算
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_sequence = -1 ^ (-1 << self.sequence_bits)

        # 位移计算
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits

        # 初始时间戳 (2025-01-01)
        self.twepoch = 1799788800000

        # 参数检查
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError(f"datacenter_id不能大于{self.max_datacenter_id}或小于0")

        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError(f"worker_id不能大于{self.max_worker_id}或小于0")

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = sequence

        # 线程锁
        self.lock = threading.Lock()

        # 上一次的时间戳
        self.last_timestamp = -1

    def _gen_timestamp(self):
        """
        生成毫秒级时间戳
        """
        return int(time.time() * 1000)

    def _til_next_millis(self, last_timestamp):
        """
        等待到下一毫秒
        """
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp

    def get_id(self):
        """
        生成唯一ID

        :return: 唯一ID
        """
        with self.lock:
            timestamp = self._gen_timestamp()

            # 如果当前时间小于上一次ID生成时间，说明系统时钟回退过，抛出异常
            if timestamp < self.last_timestamp:
                raise Exception(f"时钟向后移动，拒绝生成ID {self.last_timestamp - timestamp} 毫秒")

            # 如果是同一毫秒内生成的，则进行序号递增
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                # 如果序列号达到最大值，则等待到下一毫秒
                if self.sequence == 0:
                    timestamp = self._til_next_millis(self.last_timestamp)
            else:
                # 如果不是同一毫秒，则序列号重置
                self.sequence = 0

            self.last_timestamp = timestamp

            # 组合ID
            new_id = ((timestamp - self.twepoch) << self.timestamp_left_shift) | \
                     (self.datacenter_id << self.datacenter_id_shift) | \
                     (self.worker_id << self.worker_id_shift) | \
                     self.sequence

            # 确保返回的是正数，避免符号位为1导致的负数问题
            return new_id & 0x7FFFFFFFFFFFFFFF


# 创建全局雪花算法实例
snowflake = Snowflake(
    datacenter_id=settings.DATACENTER_ID,
    worker_id=settings.WORKER_ID,
    sequence=0
)


# 提供便捷函数
def generate_id():
    """
    生成唯一ID的便捷函数

    :return: 唯一ID
    """
    return snowflake.get_id()
