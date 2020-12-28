from rdt import RDTSocket
import time
from difflib import Differ
from Cons import RATE, FILE, CNT

client = RDTSocket(rate=RATE)
client.connect(('127.0.0.1', 2777))

data_count = 0
echo = b''
count = CNT

with open(FILE, 'r') as f:
    data = f.read()
    encoded = data.encode()
    assert len(data) == len(encoded)

start = time.perf_counter()
for i in range(count):  # send 'alice.txt' for count times
    data_count += len(data)
    client.send(encoded)

'''
blocking send works but takes more time 
'''

while True:
    reply = client.recv(2048)
    echo += reply
    print(reply)
    if len(echo) == len(encoded) * count:
        break
client.close()

'''
make sure the following is reachable
'''

print(f'transmitted {data_count * 2}bytes in {time.perf_counter() - start}s')
print(f'tr = {data_count * 2 / (time.perf_counter() - start) / 1000} KB/s\n')
print(data * count == echo.decode())
diff = Differ().compare((data * count).splitlines(keepends=True), echo.decode().splitlines(keepends=True))
for line in diff:
    assert line.startswith('  ')  # check if data is correctly echoed
