import time

from rdt import RDTSocket

start_time = time.time()
s = RDTSocket(rate=5000, debug=True)
s.bind(('127.0.0.1', 1777))
with open('231k.jpg', 'rb') as f:
    content = f.read()
for i in range(2):
    c, addr = s.accept()
    print(addr)
    c.send(content)
    c.close()
s.close()
s.block_until_close()
print('lslnb', time.time() - start_time)
