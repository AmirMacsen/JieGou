import threading
import time
from datetime import datetime

import settings


class Snowflake:
    def __init__(
        self,
        datacenter_id: int = 1,
        worker_id: int = 1,
        sequence: int = 0,
        *,
        timestamp_bits: int = 41,
        datacenter_id_bits: int = 5,
        worker_id_bits: int = 5,
        sequence_bits: int = 12,
        twepoch: int = 1735689600000,  # 2025-01-01T00:00:00Z in ms (recommended)
        signed: bool = True,
        wait_on_clock_backwards: bool = True,
        max_clock_backwards_ms: int = 5,
    ):
        """
        更安全的 Snowflake 实现，保证兼容有符号 64-bit BigInteger（<= 2**63 - 1）

        参数说明：
          - bits 可配置，但必须满足总位数 <= 63（保留符号位）
          - twepoch 以毫秒为单位，**必须** ≤ 当前时间
        """
        # 配置位宽
        self.timestamp_bits = timestamp_bits
        self.datacenter_id_bits = datacenter_id_bits
        self.worker_id_bits = worker_id_bits
        self.sequence_bits = sequence_bits

        # 校验总位数（保留 1 位符号位）
        total_bits = (
            self.timestamp_bits
            + self.datacenter_id_bits
            + self.worker_id_bits
            + self.sequence_bits
        )
        if total_bits > 63:
            raise ValueError(
                f"总位数不能超过63（当前 {total_bits}），请调整各项位宽"
            )

        # 最大值
        self.max_datacenter_id = (1 << self.datacenter_id_bits) - 1
        self.max_worker_id = (1 << self.worker_id_bits) - 1
        self.max_sequence = (1 << self.sequence_bits) - 1
        self.max_timestamp = (1 << self.timestamp_bits) - 1

        # 位移量
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = (
            self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        )

        # twepoch 校验（毫秒）
        self.twepoch = int(twepoch)
        if self.twepoch > self._gen_timestamp():
            raise ValueError(
                f"twepoch ({self.twepoch}) 在当前时间之后，请设置一个不晚于当前的 twepoch（ms）"
            )

        # 参数检查
        if datacenter_id < 0 or datacenter_id > self.max_datacenter_id:
            raise ValueError(
                f"datacenter_id 必须在 [0, {self.max_datacenter_id}] 之间"
            )
        if worker_id < 0 or worker_id > self.max_worker_id:
            raise ValueError(f"worker_id 必须在 [0, {self.max_worker_id}] 之间")

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = sequence

        # 策略选项
        self.signed = bool(signed)
        self.wait_on_clock_backwards = bool(wait_on_clock_backwards)
        self.max_clock_backwards_ms = int(max_clock_backwards_ms)

        # 线程锁与状态
        self.lock = threading.Lock()
        self.last_timestamp = -1

        # 上限（如果 signed=True，则限制到 2**63 - 1）
        self._max_id_if_signed = (1 << 63) - 1 if self.signed else None

    def _gen_timestamp(self) -> int:
        return int(time.time() * 1000)

    def _til_next_millis(self, last_ts: int) -> int:
        ts = self._gen_timestamp()
        while ts <= last_ts:
            ts = self._gen_timestamp()
        return ts

    def get_id(self) -> int:
        with self.lock:
            timestamp = self._gen_timestamp()

            # 时钟回拨处理
            if timestamp < self.last_timestamp:
                backward = self.last_timestamp - timestamp
                if self.wait_on_clock_backwards and backward <= self.max_clock_backwards_ms:
                    # 等待到下一毫秒（短暂回拨容忍）
                    timestamp = self._til_next_millis(self.last_timestamp)
                else:
                    raise RuntimeError(
                        f"时钟向后移动 {backward} ms，拒绝生成 ID"
                    )

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    # 序列耗尽，等待下一毫秒
                    timestamp = self._til_next_millis(self.last_timestamp)
            else:
                # 新毫秒，重置序列
                self.sequence = 0

            self.last_timestamp = timestamp

            # 计算时间差并校验是否溢出 timestamp_bits
            delta = timestamp - self.twepoch
            if delta < 0:
                raise RuntimeError(
                    f"当前时间小于 twepoch ({self.twepoch})，请检查 twepoch 设置"
                )
            if delta > self.max_timestamp:
                raise OverflowError(
                    f"时间戳超出可表示范围：delta={delta} > max_timestamp={self.max_timestamp}"
                )

            new_id = (
                (delta << self.timestamp_left_shift)
                | (self.datacenter_id << self.datacenter_id_shift)
                | (self.worker_id << self.worker_id_shift)
                | self.sequence
            )

            # 最终保证不超过 signed 上限（可选）
            if self.signed and new_id > self._max_id_if_signed:
                raise OverflowError(
                    f"生成的 ID 超过有符号 64-bit 上限：{new_id} > {self._max_id_if_signed}"
                )

            return new_id & 0x7FFFFFFFFFFFFFFF

    def decompose(self, id_value: int) -> dict:
        """
        将 ID 拆解为 timestamp, datacenter_id, worker_id, sequence
        返回 timestamp 为毫秒（并带 human-readable 字段）
        """
        seq = id_value & self.max_sequence
        worker = (id_value >> self.worker_id_shift) & self.max_worker_id
        dc = (id_value >> self.datacenter_id_shift) & self.max_datacenter_id
        ts_delta = (id_value >> self.timestamp_left_shift) & self.max_timestamp
        ts = ts_delta + self.twepoch
        return {
            "id": id_value,
            "timestamp": ts,
            "timestamp_human": datetime.utcfromtimestamp(ts / 1000.0).isoformat() + "Z",
            "datacenter_id": dc,
            "worker_id": worker,
            "sequence": seq,
        }


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
