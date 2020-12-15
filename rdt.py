from USocket import UnreliableSocket
from rdt_event_loop import *


class RDTSocket(UnreliableSocket):
    """
    The functions with which you are to build your RDT.
    -   recvfrom(bufsize)->bytes, addr
    -   sendto(bytes, address)
    -   bind(address)

    You can set the mode of the socket.
    -   settimeout(timeout)
    -   setblocking(flag)
    By default, a socket is created in the blocking mode. 
    https://docs.python.org/3/library/socket.html#socket-timeouts

    """

    def __init__(self, rate=None, debug=True):
        super().__init__(rate=rate)
        self._rate = rate
        self.debug = debug
        self.addr: (str, int) = None
        self.lock: threading.RLock = threading.RLock()
        self.data: bytearray = bytearray()
        self._event_loop = None

    def accept(self) -> ('RDTSocket', (str, int)):
        """
        Accept a connection. The socket must be bound to an address and listening for 
        connections. The return value is a pair (conn, address) where conn is a new 
        socket object usable to send and receive data on the connection, and address 
        is the address bound to the socket on the other end of the connection.

        This function should be blocking. 
        """
        assert self._event_loop and isinstance(self._event_loop,
                                               ServerEventLoop), 'This socket is not a listener, please bind'
        while True:
            s: SimpleRDT = self._event_loop.accept()
            if s is not None:
                return s, s.addr
            time.sleep(0.00001)

    def connect(self, address: (str, int)):
        """
        Connect to a remote socket at address.
        Corresponds to the process of establishing a connection on the client side.
        """
        assert not self._event_loop, 'Duplicated connecting or it is listening'
        self._event_loop = ClientEventLoop(self, address)
        self._event_loop.start()
        self._event_loop.put(RDTEventType.CONNECT, None)

    def recv(self, bufsize: int) -> bytes:
        """
        Receive data from the socket. 
        The return value is a bytes object representing the data received. 
        The maximum amount of data to be received at once is specified by bufsize. 
        
        Note that ONLY data send by the peer should be accepted.
        In other words, if someone else sends data to you from another address,
        it MUST NOT affect the data returned by this function.
        """

        assert self._event_loop and isinstance(self._event_loop,
                                               ClientEventLoop), "Connection not established or it is the listener"

        current = time.time()
        timeout = super(RDTSocket, self).gettimeout()
        while time.time() - current < timeout:
            with self.lock:
                recv_len = len(self.data)
                if recv_len > 0:
                    re = self.data[:bufsize]
                    self.data = self.data[bufsize:]
                    return re
            time.sleep(0.00001)

        raise TimeoutError()

    def send(self, _bytes: bytes):
        """
        Send data to the socket. 
        The socket must be connected to a remote socket, i.e. self._send_to must not be none.
        """
        assert self._event_loop and isinstance(self._event_loop, ClientEventLoop), "Connection not established yet."
        self._event_loop.put(RDTEventType.SEND, (self.addr, _bytes))

    def close(self):
        """
        Finish the connection and release resources. For simplicity, assume that
        after a socket is closed, neither futher sends nor receives are allowed.
        """
        if self._event_loop:
            self._event_loop.close()
        else:
            super().close()

    def force_close(self):
        super(RDTSocket, self).close()

    def bind(self, address: (str, int)):
        assert self._event_loop is None, 'Can not duplicate binding'
        super(RDTSocket, self).bind(address)
        self._event_loop = ServerEventLoop(self)
        self._event_loop.start()

    def create_simple_socket(self, remote: (str, int), recv_offset: int, send_offset: int) -> 'SimpleRDT':
        return SimpleRDT(self._rate, self.debug, recv_offset, send_offset, remote, self._event_loop.event_queue)


class SimpleRDT(RDTSocket):

    def __init__(self, rate, debug, recv_offset: int, send_offset: int, remote: (str, int), event_queue: SimpleQueue):
        super(SimpleRDT, self).__init__(rate, debug)
        self.send_buffer = {}
        self.send_offset = send_offset
        self.send_success_offset = send_offset
        self.event_queue = event_queue
        self.addr = remote
        self.last_ack = 0
        self.recv_buffer = []
        self.recv_offset = recv_offset
        self.status = None
        self.__is_close = False

    def close(self):
        assert not self.__is_close, 'Duplicated close'
        self.__is_close = True
        self.event_queue.put(RDTEvent(RDTEventType.SIMPLE_CLOSE, self.addr))

    def send(self, _bytes: bytes):
        assert not self.__is_close, 'Closed!'
        self.event_queue.put(RDTEvent(RDTEventType.SEND, (self.addr, _bytes)))

    def recv(self, bufsize: int) -> bytes:
        assert not self.__is_close, 'Closed!'
        current = time.time()
        timeout = super().gettimeout()
        while time.time() - current < timeout:
            with self.lock:
                if len(self.data) > 0:
                    re = self.data[:bufsize]
                    self.data = self.data[bufsize:]
                    return re
            time.sleep(0.00001)

        raise TimeoutError()

    def connect(self, address: (str, int)):
        assert False, 'Duplicated connecting'

    def accept(self) -> ('RDTSocket', (str, int)):
        assert False, 'It is not listening'


"""
You can define additional functions and classes to do thing such as packing/unpacking packets, or threading.

"""
