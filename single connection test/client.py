from Cons import *
from rdt import RDTSocket
import time
from difflib import Differ

client = RDTSocket(debug=DEBUG, rate=RATE)
client.bind(('127.0.0.1', 9998))
client.connect(('127.0.0.1', 9999))

data_count = 0
echo = b''
count = CNT

with open(FILE, 'rb') as f:
    data = f.read()
    encoded = data
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
# client.save_perf('100K_c_l_10k.json')
diff = Differ().compare((data * count).splitlines(keepends=True), echo.splitlines(keepends=True))
for line in diff:
    assert line.startswith('  ')  # check if data is correctly echoed
