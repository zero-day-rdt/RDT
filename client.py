from rdt import RDTSocket

c = RDTSocket(rate=1000, debug=True)
c.connect(('127.0.0.1', 1777))
with open('rdt.py', 'rb') as f:
    c.send(f.read())
print(c.recv(1000))
