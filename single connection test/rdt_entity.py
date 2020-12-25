import struct
from enum import Enum
from functools import reduce
import time


class RDTEventType(Enum):
    SYN = 0  # 对方SYN, 下同
    SYN_ACK = 1
    ACK = 2
    FIN = 3
    FIN_ACK = 4
    RST = 5
    SAK = 6
    CORRUPTION = 7
    SEND_ACK = 8  # 需要 send ACK
    SEND_FIN = 10  # 需要 send FIN
    UNKNOWN_ERROR = 11  # 在 send loop 或 recv loop 捕获的异常，未知类型
    ACK_TIMEOUT = 12  # 等待ACK超时
    CONNECT = 13  # 上层调用CONNECT
    SEND = 14  # 上层调用SEND
    LISTEN_CLOSE = 15  # 对监听的调用 CLOSE
    SIMPLE_CLOSE = 16  # 调用CLOSE
    DESTROY_SIMPLE = 17  # 销毁单个连接
    DESTROY_ALL = 18  # 尝试结束所有循环线程，探测到可以结束时会引发VANISH事件
    VANISH = 19  # 真正结束所有线程，这个事件会break掉事件循环


class RDTConnectionStatus(Enum):
    SYN_ = 0  # 收到过SYN了
    SYN_ACK_ = 1  # 收到过SYN_ACK了
    ACK_ = 2  # 收到过ACK了
    FIN = 3  # 发过FIN了
    FIN_ = 4  # 收到过FIN了
    FIN_ACK_ = 5  # 收到过FIN_ACK了


class RDTEvent:

    def __init__(self, e_type: RDTEventType, body: any):
        self.type = e_type
        self.body = body


class RDTTimer:

    def __init__(self, timeout: float, e: RDTEvent):
        self.start_time = time.time()
        self.event = e
        self.target_time = self.start_time + timeout
        self.active = True


class RDTPacket:
    def __init__(self, remote, SEQ, SEQ_ACK, SYN=0, ACK=0, FIN=0, RST=0, SAK=0, _=0, PAYLOAD=bytes()):
        self.SYN = SYN
        self.ACK = ACK
        self.FIN = FIN
        self.RST = RST
        self.SAK = SAK
        self._ = _
        self.SEQ = SEQ
        self.SEQ_ACK = SEQ_ACK
        self.LEN = len(PAYLOAD)
        self.CHECKSUM = 0
        self.PAYLOAD: bytes = PAYLOAD
        self.PAYLOAD_REAL: bytes = self.PAYLOAD
        self.remote = remote
        self.__packet: bytearray = bytearray()

    def make_packet(self):
        self.__packet = bytearray()
        self.__packet += ((self.SYN << 7) + (self.ACK << 6) + (self.FIN << 5) + (self.RST << 4) +
                          (self.SAK << 3) + self._).to_bytes(1, 'big')
        self.__packet += struct.pack('!2I2H', self.SEQ, self.SEQ_ACK, self.LEN, 0)  # CHECKSUM
        extra = (4 - self.LEN % 4) % 4
        self.PAYLOAD_REAL = self.PAYLOAD + b'\x00' * extra
        self.CHECKSUM = self._checksum()

        self.__packet[-2:] = struct.pack('!H', self.CHECKSUM)
        self.__packet += self.PAYLOAD_REAL
        return self.__packet

    @staticmethod
    def resolve(bs: bytearray, addr: (str, int)) -> 'RDTPacket':
        r: RDTPacket = RDTPacket(remote=addr, SEQ=0, SEQ_ACK=0)
        bits, r.SEQ, r.SEQ_ACK, r.LEN, r.CHECKSUM = struct.unpack('!B2I2H', bs[:13])
        r.SYN, r.ACK, r.FIN, = (bits >> 7) & 1, (bits >> 6) & 1, (bits >> 5) & 1
        r.RST, r.SAK, r._ = (bits >> 4) & 1, (bits >> 3) & 1, bits & 0x7

        r.PAYLOAD_REAL = bs[13:]
        return r

    def _checksum(self) -> int:
        bs = self.PAYLOAD_REAL
        checksum = (self.SYN << 7 + self.ACK << 6 + self.FIN << 5 + self.RST << 4 + self.SAK << 3 + self._) << 24
        checksum += self.SEQ + self.SEQ_ACK + (self.LEN << 16)
        if len(bs) > 0:
            for i in range(0, len(bs), 4):
                checksum += (bs[i] << 24) + (bs[i + 1] << 16) + (bs[i + 2] << 8) + bs[i + 3]
        while checksum > 0xFFFF:
            checksum = (checksum % 0xFFFF) + (checksum // 0xFFFF)
        return checksum

    def check(self) -> bool:
        if len(self.PAYLOAD_REAL) % 4 != 0:
            return False
        check = self._checksum()
        self.PAYLOAD = self.PAYLOAD_REAL[:self.LEN]
        if check != self.CHECKSUM or self._ != 0:
            return False

        return True
