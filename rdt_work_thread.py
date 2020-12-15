import threading
import time
from rdt import RDTSocket
from queue import *

from rdt_entity import *
from rdt_event_loop import EventLoop
from rdt_entity import RDTPacket


class SendLoop(threading.Thread):
    def __init__(self, rdt_socket: RDTSocket, event_loop: EventLoop):
        super().__init__()
        self.socket: RDTSocket = rdt_socket
        self.send_queue: SimpleQueue = SimpleQueue()
        self.event_loop = event_loop

    def run(self) -> None:
        while True:
            try:
                if not self.send_queue.empty():
                    try:
                        pkt: RDTPacket = self.send_queue.get_nowait()
                        if pkt == 0:
                            break
                        _bytes = pkt.make_packet()
                        self.socket.sendto(_bytes, pkt.remote)
                        self.event_loop.put(RDTEventType.SEND_SUCCESS, pkt)
                    except Empty:
                        pass
                else:
                    time.sleep(0.00001)
            except Exception as e:
                self.event_loop.put(RDTEventType.UNKNOWN_ERROR, e)

    def put(self, e):
        self.send_queue.put(e)


class RecvLoop(threading.Thread):
    def __init__(self, rdt_socket: RDTSocket, event_loop: EventLoop):
        super().__init__()
        self.socket: RDTSocket = rdt_socket
        self.event_queue = SimpleQueue()
        self.event_loop = event_loop

    def run(self) -> None:
        while self.event_queue.empty():
            try:
                rec, addr = self.socket.recvfrom(0xff)
                pkt = RDTPacket.resolve(rec, addr)
                if pkt.check():
                    if pkt.SYN == 1:
                        if pkt.ACK == 0:
                            self.event_loop.put(RDTEventType.SYN, pkt)
                        else:
                            self.event_loop.put(RDTEventType.SYN_ACK, pkt)
                    elif pkt.FIN == 1:
                        if pkt.ACK == 0:
                            self.event_loop.put(RDTEventType.FIN, pkt)
                        else:
                            self.event_loop.put(RDTEventType.FIN_ACK, pkt)
                    elif pkt.RST == 1:
                        self.event_loop.put(RDTEventType.RST, pkt)
                    elif pkt.ACK == 1:
                        self.event_loop.put(RDTEventType.ACK, pkt)
                    else:
                        self.event_loop.put(RDTEventType.CORRUPTION, pkt)
                else:
                    self.event_loop.put(RDTEventType.CORRUPTION, pkt)
            except Exception as e:
                self.event_loop.put(RDTEventType.UNKNOWN_ERROR, e)
