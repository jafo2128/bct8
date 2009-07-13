from subprocess import Popen, PIPE
from threading import Thread
from traceback import format_exc
from select import select
from socket import *
from time import clock
import struct
import sys

CHUNKSIZE = 1024

mcast = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
mcast.bind(('', 9200))
mreq = struct.pack('4sl', inet_aton('224.0.1.20'), INADDR_ANY)
mcast.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

class Relay(object):
    def __init__(self):
        self.sock = socket()
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(('', 9201))
        self.sock.listen(5)
        self.clients = {}

    def accept_loop(self):
        while True:
            client_sock, client_addr = self.sock.accept()
            self.clients[client_sock] = client_addr
            print 'Accepted connection from', client_addr

    def run(self):
        while True:
            data = mcast.recv(1024)
            writable = select([], self.clients.keys(), [], 0.1)[1]
            for sock in writable:
                try:
                    sock.send(data)
                except:
                    if sock in self.clients:
                        print 'Disconnected', self.clients[sock]
                        del self.clients[sock]

r = Relay()
t1 = Thread(target=r.accept_loop)
t1.setDaemon(True)
t1.start()
r.run()
