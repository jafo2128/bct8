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

c.execute('SELECT * FROM trs_talkgroup WHERE sid=? AND alpha LIKE "SFPD A%" ORDER BY decid', (SID,))
bank = 0
num = 1
for id, sid, decid, alpha, description, mode in c:
    tbank = chr(bank + ord('A'))
    tnum = num % 10
    cmd = 'IC %s%i %s\n' % (tbank, tnum, str(decid).rjust(6, '0'))
    print alpha.ljust(20, ' '), cmd,
    sock.sendall(cmd)
    sleep(0.1)

    num += 1
    if num > 10:
        num = 1
        bank += 1

while bank < 5:
    tbank = chr(bank + ord('A'))
    tnum = num % 10
    cmd = 'IC %s%i 000000\n' % (tbank, tnum)
    print 'FILL'.ljust(20, ' '), cmd,
    sock.sendall(cmd)
    sleep(0.1)

    num += 1
    if num > 10:
        num = 1
        bank += 1
