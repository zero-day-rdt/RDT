from rdt import RDTSocket

s = RDTSocket(rate=1000, debug=True)
s.bind(('127.0.0.1', 1777))
while True:
    c, addr = s.accept()
    print(addr)
    print(c.recv(1000).decode('utf-8'))
    c.close()
