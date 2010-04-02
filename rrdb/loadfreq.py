from socket import socket
from time import sleep
import sqlite3
import sys

SID = int(sys.argv[1])

conn = sqlite3.connect('radioreference.db')
c = conn.cursor()

def readlines(s):
    buffer = ''
    while True:
        buffer += sock.recv(1024)
        while buffer.find('\n') != -1:
            line, buffer = buffer.split('\n', 1)
            yield line.rstrip('\r')
    return

sock = socket()
sock.connect(('127.0.0.1', 9200))

c.execute('SELECT * FROM trs_freq WHERE sid=? AND freq != 0.0 ORDER BY freq', (SID,))
num = 1
for sid, site, use, freq in c:
    high, low = freq.split('.', 1)
    high = high.rjust(4, '0')
    low = low.ljust(4, '0')
    cmd = 'PM%03iT%s\n' % (num, high + low)
    print cmd,
    sock.sendall(cmd)
    for line in readlines(sock):
        if line.startswith('C%03i' % num): break
    num += 1

while num < 250:
    cmd = 'PM%03i 00000000\n' % num
    print cmd,
    sock.sendall(cmd)
    for line in readlines(sock):
        if line.startswith('C%03i' % num): break
    num += 1
