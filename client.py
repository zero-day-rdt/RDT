from rdt import RDTSocket
import time

current = time.time()
c = RDTSocket(rate=5000, debug=True)
c.connect(('127.0.0.1', 1777))
bs = bytearray()
i = c.recv(1024)
while len(i) > 0:
    bs.extend(i)
    i = c.recv(1024)
c.close()
c.block_until_close()
print('结束: ', time.time() - current)
