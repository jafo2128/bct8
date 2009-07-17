from daemon import become_daemon
from threading import Thread
from select import select
from socket import *

from serial import Serial

class ControlServer(object):
    def __init__(self, device='/dev/ttyUSB0', baud=57600):
        self.serial = Serial(device, baud, timeout=0.1)
        self.buf = ''

        self.clients = {}
        self.server = socket()
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.bind(('0.0.0.0', 9200))
        self.server.listen(5)

    def write(self, cmd):
        self.serial.write(cmd + '\r')

    def accept_loop(self):
        while True:
            sock, addr = self.server.accept()
            self.clients[sock] = addr
            print 'Accepted', self.clients[sock]

    def run(self):
        while True:
            readable = select(self.clients.keys(), [], [], 0.1)[0]
            for sock in readable:
                data = sock.recv(1024)
                if not data:
                    print 'Disconnected', self.clients[sock]
                    del self.clients[sock]
                    continue
                data = data.rstrip('\r\n')
                self.write(data)
            readable = select([self.serial], [], [], 0.1)[0]
            for serial in readable:
                self.buf += serial.read(1024)
                while self.buf.find('\r') != -1:
                    line, self.buf = self.buf.split('\r', 1)
                    for sock in self.clients.keys():
                        sock.send(line + '\n')

def main():
    control = ControlServer()

    t1 = Thread(target=control.accept_loop, args=[])
    t1.setDaemon(True)
    t1.start()

    control.run()

if __name__ == '__main__':
    logfd = file('radio.log', 'a')
    become_daemon(out_log=logfd, err_log=logfd)
    main()
