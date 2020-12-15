import threading
from queue import SimpleQueue, Empty
import time
from rdt_entity import *
from rdt import RDTSocket, SimpleRDT
from rdt_work_thread import SendLoop, RecvLoop
import random

SEND_WAIT = 0.001


class EventLoop(threading.Thread):
    def __init__(self, _socket: RDTSocket):
        super().__init__()
        self.socket: RDTSocket = _socket
        self.event_queue: SimpleQueue = SimpleQueue()
        self.send_loop: SendLoop = SendLoop(_socket, self)
        self.recv_loop: RecvLoop = RecvLoop(_socket, self)
        self.timers = []

    def run(self) -> None:
        while True:
            if len(self.timers) > 0:
                while self.timers[0]['t'] <= time.time():
                    timer = self.timers.pop()
                    self.event_queue.put_nowait(timer['e'])
            if self.event_queue.empty():
                time.sleep(0.00001)
            else:
                try:
                    e: RDTEvent = self.event_queue.get_nowait()
                    if e.type == RDTEventType.SIMPLE_CLOSE:
                        self.close()
                        break
                    elif e.type == RDTEventType.SEND_ACK:
                        self.on_send_ack(e.body)
                    elif e.type == RDTEventType.SEND_FIN:
                        self.on_send_fin(e.body)
                    elif e.type == RDTEventType.SAK:
                        self.on_sak(e.body)
                    elif e.type == RDTEventType.SEND_SAK:
                        self.on_send_sak(e.body)
                    elif e.type == RDTEventType.SEND_SUCCESS:
                        self.on_send_success(e.body)
                    elif e.type == RDTEventType.SEND:
                        self.on_send(e.body)
                    elif e.type == RDTEventType.CONNECT:
                        self.on_connect(e.body)
                    elif e.type == RDTEventType.CORRUPTION:
                        self.on_corruption(e.body)
                    elif e.type == RDTEventType.ACK_TIMEOUT:
                        self.on_ack_timeout(e.body)
                    elif e.type == RDTEventType.ACCEPT_TIMEOUT:
                        self.on_accept_timeout()
                    elif e.type == RDTEventType.RST:
                        self.on_rst(e.body)
                    elif e.type == RDTEventType.UNKNOWN_ERROR:
                        self.on_unknown_error(e.body)
                    elif e.type == RDTEventType.FIN_ACK:
                        self.on_fin_ack(e.body)
                    elif e.type == RDTEventType.FIN:
                        self.on_fin(e.body)
                    elif e.type == RDTEventType.ACK:
                        self.on_ack(e.body)
                    elif e.type == RDTEventType.SYN_ACK:
                        self.on_syn_ack(e.body)
                    elif e.type == RDTEventType.SYN:
                        self.on_syn(e.body)
                    else:
                        self.on_sb()
                except Empty:
                    pass
                except Exception as e:
                    print(e)

    def close(self):
        self.send_loop.put(0)
        self.recv_loop.event_queue.put(0)
        self.socket.force_close()

    def put(self, e_type: RDTEventType, e_args):
        self.event_queue.put(RDTEvent(e_type, e_args))

    def get_nowait(self) -> RDTEvent:
        return self.event_queue.get_nowait()

    def on_sb(self):
        pass  # ???

    def on_connect(self, remote: (str, int)):
        pass  # 主动握手

    def on_corruption(self, pkt: RDTPacket):
        pass  # 包炸了

    def on_ack_timeout(self, pkt: RDTPacket):
        pass  # 等ACK超时了

    def on_accept_timeout(self):
        pass  # 上层accept超时了

    def on_rst(self, pkt: RDTPacket):
        pass  # remote 拒绝了

    def on_unknown_error(self, error: Exception):
        pass  # send loop 或 recv loop 报错了

    def on_fin_ack(self, pkt: RDTPacket):
        pass  # remote 挥手成功

    def on_fin(self, pkt: RDTPacket):
        pass  # remote 试图挥手

    def on_ack(self, pkt: RDTPacket):
        pass  # 正常收包

    def on_syn(self, pkt: RDTPacket):
        pass  # 有 remote 来SYN了

    def on_syn_ack(self, pkt: RDTPacket):
        pass  # 对方接受握手

    def on_send(self, bs: bytes):
        pass  # 发给 send loop

    def on_send_success(self, pkt: RDTPacket):
        pass  # 启动计时器

    def on_send_sak(self, pkt: RDTPacket):
        pass  # 发送SAK包

    def on_sak(self, pkt: RDTPacket):
        pass  # 收了个SAK包

    def on_send_fin(self, remote: (str, int)):
        pass  # 发送FIN包

    def on_send_ack(self, body: (int, (str, int))):
        pass  # 延时到了，判断是否发送ack

    def push_timer(self, timeout: float, e: RDTEvent):
        index = 0
        _ = {
            't': time.time() + timeout,
            'e': e
        }
        while len(self.timers) > index:
            if self.timers[index]['t'] <= _['t']:
                index += 1
            else:
                self.timers.insert(index, _)
                return
        self.timers.append(_)

    def put_send_sak(self, seq_sak: int, seq_ack: int, remote: (str, int)):
        sak_pkt = RDTPacket(SAK=1, SEQ=seq_sak, SEQ_ACK=seq_ack, remote=remote)
        self.put(RDTEventType.SEND_SAK, sak_pkt)

    def put_send_ack(self, seq_ack: int, remote: (str, int)):
        self.push_timer(SEND_WAIT, RDTEvent(RDTEventType.SEND_ACK, (seq_ack, remote)))

    def put_send_fin(self, remote: (str, int)):
        self.push_timer(SEND_WAIT, RDTEvent(RDTEventType.SEND_FIN, remote))


class ServerEventLoop(EventLoop):
    def __init__(self, listen_socket: RDTSocket):
        super().__init__(listen_socket)
        self.connections: dict = {}
        self.accept_queue = SimpleQueue()

    def accept(self) -> (RDTSocket, (str, int)):
        if not self.accept_queue.empty():
            try:
                return self.accept_queue.get_nowait()
            except Empty as e:
                print(e)

    def on_syn(self, pkt: RDTPacket):
        remote = pkt.remote
        assert remote not in self.connections, 'Has SYN'
        simple_sct = self.socket.create_simple_socket(remote, pkt.SEQ, random.randint(0, 1000000))
        simple_sct.status = RDTConnectionStatus.SYN_
        self.connections[remote] = simple_sct
        syn_ack_pkt = RDTPacket(SYN=1, ACK=1, remote=remote)
        self.put(RDTEventType.SEND, syn_ack_pkt)

    def on_syn_ack(self, pkt: RDTPacket):
        raise AssertionError('impossible syn ack')

    def on_ack(self, pkt: RDTPacket):
        remote = pkt.remote
        assert remote in self.connections, 'No such connection'
        simple_sct: SimpleRDT = self.connections[remote]
        if simple_sct.status == RDTConnectionStatus.SYN_:
            self.accept_queue.put(simple_sct)
            simple_sct.status = RDTConnectionStatus.ACK_
        else:
            return  # FIN或者FIN_ACK了，那就不要了
        if pkt.SEQ == simple_sct.recv_offset:
            with self.socket.lock:
                simple_sct.data.extend(pkt.PAYLOAD)  # 放进对应连接的接受数据里
            simple_sct.recv_offset += pkt.LEN
            while len(simple_sct.recv_buffer) > 0 and simple_sct.recv_buffer[0].SEQ == simple_sct.recv_offset:
                pkt = simple_sct.recv_buffer.pop()
                with self.socket.lock:
                    simple_sct.data.extend(pkt.PAYLOAD)
                simple_sct.recv_offset += pkt.LEN
            self.put_send_ack(simple_sct.recv_offset, remote)
        elif pkt.SEQ > simple_sct.recv_offset:
            index = 0
            while len(simple_sct.recv_buffer) > index:
                if simple_sct.recv_buffer[index].SEQ < pkt.SEQ:
                    index += 1
                elif simple_sct.recv_buffer[index].SEQ == pkt.SEQ:
                    return
                else:
                    simple_sct.recv_buffer.insert(index, pkt)
                    self.put_send_sak(pkt.SEQ, seq_ack=simple_sct.last_ack, remote=remote)
                    return
            simple_sct.recv_buffer.append(pkt)
            self.put_send_sak(pkt.SEQ, seq_ack=simple_sct.last_ack, remote=remote)

    def on_fin(self, pkt: RDTPacket):
        remote = pkt.remote
        assert remote in self.connections, 'No such connection'
        simple_sct: SimpleRDT = self.connections[remote]
        if simple_sct.status < RDTConnectionStatus.FIN_:
            simple_sct.status = RDTConnectionStatus.FIN_
        else:
            return  # FIN或者FIN ACK过了
        self.put_send_ack(simple_sct.recv_offset, remote)
        self.put_send_fin(remote)

    def on_fin_ack(self, pkt: RDTPacket):
        remote = pkt.remote
        assert remote in self.connections, 'No such connection'
        simple_sct: SimpleRDT = self.connections[remote]
        if simple_sct.status < RDTConnectionStatus.FIN_ACK_:
            simple_sct.status = RDTConnectionStatus.FIN_ACK_
        else:
            return  # FIN ACK过了
        self.put(RDTEventType.DESTROY_SIMPLE, remote)

    def on_send(self, r: ((str, int), bytes)):
        remote, bs = r
        simple_sct: SimpleRDT = self.connections[remote]
        if simple_sct.status < RDTConnectionStatus.ACK_:
            return
        pkt = RDTPacket(ACK=1, SEQ=simple_sct.send_offset, SEQ_ACK=simple_sct.recv_offset, PAYLOAD=bs, remote=remote)
        simple_sct.last_ack = pkt.SEQ_ACK

    def on_send_success(self, pkt: RDTPacket):
        remote = pkt.remote
        assert remote in self.connections, 'No such connection'
        simple_sct: SimpleRDT = self.connections[remote]
        simple_sct.last_ack = pkt.SEQ_ACK

    def on_send_ack(self, body: (int, (str, int))):
        pass  # TODO

    def close(self):
        super(ServerEventLoop, self).close()


class ClientEventLoop(EventLoop):
    def __init__(self, connection_socket: RDTSocket, remote: (str, int)):
        super().__init__(connection_socket)
        self.remote = remote
        self.send_buffer: dict = {}
        self.recv_buffer: dict = {}

    def close(self):
        super(ClientEventLoop, self).close()
