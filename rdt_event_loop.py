import threading
from queue import SimpleQueue, Empty
import time
from rdt_entity import *
from rdt import RDTSocket
from rdt_work_thread import SendLoop, RecvLoop


class EventLoop(threading.Thread):
    def __init__(self, _socket: RDTSocket):
        super().__init__()
        self.socket: RDTSocket = _socket
        self.event_queue: SimpleQueue = SimpleQueue()
        self.send_loop: SendLoop = SendLoop(_socket, self)
        self.recv_loop: RecvLoop = RecvLoop(_socket, self)
        self.send_buffer: dict = {}
        self.recv_buffer: dict = {}

    def close(self):
        self.send_loop.put(0)
        self.recv_loop.event_queue.put(0)
        self.socket.force_close()

    def put(self, e_type: RDTEventType, e_args):
        self.event_queue.put(RDTEvent(e_type, e_args))

    def get_nowait(self) -> RDTEvent:
        return self.event_queue.get_nowait()


class ServerEventLoop(EventLoop):
    def __init__(self, listen_socket: RDTSocket):
        super().__init__(listen_socket)

    def run(self) -> None:
        while True:
            if self.event_queue.empty():
                time.sleep(0.00001)
            else:
                try:
                    e: RDTEvent = self.event_queue.get_nowait()
                    if e.type == RDTEventType.CLOSE:
                        self.close()
                        break
                    elif e.type == RDTEventType.SEND_SUCCESS:
                        pass  # 启动计时器
                    elif e.type == RDTEventType.SEND:
                        pass  # 发给 send loop
                    elif e.type == RDTEventType.CONNECT:
                        pass  # 这是无效事件
                    elif e.type == RDTEventType.CORRUPTION:
                        pass  # 包炸了
                    elif e.type == RDTEventType.ACK_TIMEOUT:
                        pass  # 等ACK超时了
                    elif e.type == RDTEventType.ACCEPT_TIMEOUT:
                        pass  # 上层accept超时了
                    elif e.type == RDTEventType.RST:
                        pass  # remote 拒绝了
                    elif e.type == RDTEventType.UNKNOWN_ERROR:
                        pass  # send loop 或 recv loop 报错了
                    elif e.type == RDTEventType.FIN_ACK:
                        pass  # remote 挥手成功
                    elif e.type == RDTEventType.FIN:
                        pass  # remote 试图挥手
                    elif e.type == RDTEventType.ACK:
                        pass  # 正常收包
                    elif e.type == RDTEventType.SYN_ACK:
                        pass  # 这是无效事件，一定是对方主动SYN
                    elif e.type == RDTEventType.SYN:
                        pass  # 有 remote 来SYN了
                    else:
                        pass # 我直接问号
                except Empty:
                    pass

    def accept(self) -> (RDTSocket, (str, int)):
        pass

    def close(self):
        super(ServerEventLoop, self).close()
        # TODO


class ClientEventLoop(EventLoop):
    def __init__(self, connection_socket: RDTSocket, remote: (str, int)):
        super().__init__(connection_socket)
        self.remote = remote

    def run(self) -> None:
        while True:
            if self.event_queue.empty():
                time.sleep(0.00001)
            else:
                try:
                    e: RDTEvent = self.event_queue.get_nowait()
                    if e.type == RDTEventType.CLOSE:
                        self.close()
                        break
                    elif e.type == RDTEventType.SEND:
                        self.send_loop.put(e.args)
                except Empty:
                    pass

    def close(self):
        super(ClientEventLoop, self).close()
        # TODO
