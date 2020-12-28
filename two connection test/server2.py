from rdt import RDTSocket
import time
from Cons import RATE

if __name__=='__main__':
    server = RDTSocket(rate=RATE)
    server.bind(('127.0.0.1', 2777))

    while True:
        conn, client_addr = server.accept()
        start = time.perf_counter()
        while True:
            data = conn.recv(2048)
            if data:
                conn.send(data)
            else:
                break
        '''
        make sure the following is reachable
        '''
        conn.close()
        print(f'connection finished in {time.perf_counter()-start}s')