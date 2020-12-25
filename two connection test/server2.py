import time

start_time = time.time()
s = RDTSocket(rate=50000, debug=True)
s.bind(('127.0.0.1', 2777))
with open('../1700k.jpg', 'rb') as f:
    content = f.read()
for i in range(5):
    c, addr = s.accept()
    print(addr)
    c.send(content)
    c.close()
s.close()
s.block_until_close()
print('lslnb', time.time() - start_time)
