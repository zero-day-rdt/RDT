from rdt import RDTSocket

c = RDTSocket(rate=10000, debug=True)
c.connect(('127.0.0.1', 1777))
c.send(b'lslnb')
print(c.recv(1000))
