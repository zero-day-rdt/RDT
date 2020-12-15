from enum import Enum


class RDTEventType(Enum):
    SYN = 0
    SYN_ACK = 1
    ACK = 2
    FIN = 3
    FIN_ACK = 4
    UNKNOWN_ERROR = 5
    RST = 6
    ACCEPT_TIMEOUT = 7
    ACK_TIMEOUT = 8
    CORRUPTION = 9
    CONNECT = 10
    SEND = 11
    SEND_SUCCESS = 12
    CLOSE = 13


class RDTConnectionStatus(Enum):
    _SYN = 0
    _SYN_ACK = 1
    _FIN = 2
    _FIN_ACK = 3


class RDTEvent:

    def __init__(self, e_type: RDTEventType, args: tuple):
        self.type = e_type
        self.args = args
