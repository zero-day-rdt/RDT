import struct
from functools import reduce


class RDT_Packet:
    def __init__(self):
        self.SYN = 0
        self.ACK = 0
        self.FIN = 0
        self.RST = 0
        self._ = 0
        self.SEQ = 0
        self.SEQ_ACK = 0
        self.LEN = 0
        self.CHECKSUM = 0
        self.content = ''
        self.PAYLOAD: bytes = bytes()
        self.addr = ('', -1)
        self.packet: bytearray = bytearray()

    def _make_head(self):
        self.packet = bytearray()
        self.packet += self.SYN << 7 + self.ACK << 6 + self.FIN << 5 + self.RST << 4 + self._
        self.packet += struct.pack('!2I2H', self.SEQ, self.SEQ_ACK, self.LEN, 0)  # CHECKSUM

    def make_packet(self):
        self._make_head()

        p_len = len(self.content)
        extra = (4 - p_len % 4) % 4
        self.content += '\x00' * extra
        self.PAYLOAD = self.content.encode('utf-8')
        self.CHECKSUM = RDT_Packet._checksum(self.PAYLOAD)

        self.packet[-2:] = struct.pack('!H', self.CHECKSUM)
        self.packet += self.PAYLOAD
        return self.packet

    @staticmethod
    def resolve(bs: bytearray, addr: (str, int)) -> 'RDT_Packet':
        r: RDT_Packet = RDT_Packet()
        bits, r.SEQ, r.SEQ_ACK, r.LEN, r.CHECKSUM = struct.unpack('!B2I2H', bs[:13])
        r.SYN, r.ACK, r.FIN, r.RST, r._ = (bits >> 7) & 1, (bits >> 6) & 1, (bits >> 5) & 1, (bits >> 4) & 1, bits & 0xF
        r.PAYLOAD = bs[13:]
        r.addr = addr
        return r

    @staticmethod
    def _checksum(bs: bytes) -> int:
        checksum = reduce(lambda x, y: x + y, struct.unpack('!%dI' % (len(bs) // 4), bs))
        while checksum > 0xFFFF:
            checksum = checksum % 0xFFFF + checksum // 0xFFFF
        return checksum

    def check(self) -> bool:
        if len(self.PAYLOAD) % 4 != 0:
            return False
        check = RDT_Packet._checksum(self.PAYLOAD)
        if check != self.CHECKSUM or self._ != 0:
            return False
        self.content = self.PAYLOAD[:self.LEN].decode('utf-8')

        return True
