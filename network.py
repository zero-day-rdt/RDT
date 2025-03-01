from socket import inet_aton, inet_ntoa
import random, time
import threading
from socketserver import ThreadingUDPServer
from Cons import *

lock = threading.Lock()


def bytes_to_addr(bytes):
    return inet_ntoa(bytes[:4]), int.from_bytes(bytes[4:8], 'big')


def addr_to_bytes(addr):
    return inet_aton(addr[0]) + addr[1].to_bytes(4, 'big')


class Server(ThreadingUDPServer):
    def __init__(self, addr, rate=None, delay=None):
        super().__init__(addr, None)
        self.rate = rate
        self.buffer = 0
        self.delay = delay

    def verify_request(self, request, client_address):
        """
        request is a tuple (data, socket)
        data is the received bytes object
        socket is new socket created automatically to handle the request

        if this function returns False， the request will not be processed, i.e. is discarded.
        details: https://docs.python.org/3/library/socketserver.html
        """
        # return True
        if self.buffer < BUFFER:  # some finite buffer size (in bytes) #change1
            self.buffer += len(request[0])
            return True
        else:
            print('爆炸了')
            return False

    def finish_request(self, request, client_address):
        data, socket = request

        with lock:
            if random.random() < LOSS:  # change1
                self.buffer -= len(data)
                return
            if self.rate:
                time.sleep(len(data) / self.rate)
            self.buffer -= len(data)
            """
            blockingly process each request
            you can add random loss/corrupt here

            for example:
            if random.random() < loss_rate:
                return 
            for i in range(len(data)-1):
                if random.random() < corrupt_rate:
                    data[i] = data[:i] + (data[i]+1).to_bytes(1,'big) + data[i+1:]
            """

        """
        this part is not blocking and is executed by multiple threads in parallel
        you can add random delay here, this would change the order of arrival at the receiver side.
        
        for example:
        time.sleep(random.random())
        """

        to = bytes_to_addr(data[:8])
        dara = bytearray(data)
        print(client_address, to)  # observe tht traffic
        for i in range(len(data[8:])):
            if random.random() < CORRUPTION:
                dara[i + 8] = data[i + 8] ^ 0x7F
                print('corruption')
        socket.sendto(addr_to_bytes(client_address) + dara[8:], to)


server_address = ('127.0.0.1', 12345)

if __name__ == '__main__':
    with Server(server_address, rate=RATE) as server:  # change1
        server.serve_forever()
