from socket import socket
from select import select
from time import sleep
import sys

sock = socket()
sock.connect(('192.168.1.7', 9200))

for line in file(sys.argv[1], 'r'):
    line = line.rstrip('\r\n') + '\r'
    sock.send(line + '\n')
    line = ''
    while not line.startswith('C'):
        line = sock.recv(1024)
        print repr(line)
