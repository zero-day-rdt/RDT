from rdt import RDTSocket

s = RDTSocket(rate=10000, debug=True)
s.bind(('127.0.0.1', 1777))
c, addr = s.accept()
print(addr)
s.close()
print(c.recv(1000).decode('utf-8'))
c.close()
