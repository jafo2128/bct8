from socket import socket
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

for line in readlines(sock):
    if not line.startswith('ID'): continue
    squelch, tgid, freq = line.split(' ', 3)[1:]
    if squelch == 'S':
        squelch = True
    else:
        squelch = False
    tgid = int(tgid.lstrip('0'))
    if squelch:
        c.execute('SELECT * FROM trs_talkgroup WHERE sid=? AND decid=?', (SID, tgid))
        talkgroup = c.fetchall()
        if not talkgroup:
            print 'Unknown talkgroup:', tgid
        else:
            for id, sid, decid, alpha, desc, mode in talkgroup:
                if not alpha:
                    alpha = '-----'
                print alpha.ljust(16, ' '), desc
