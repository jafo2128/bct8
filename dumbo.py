from subprocess import Popen, PIPE
from traceback import format_exc
from threading import Thread
from select import select
from socket import *
import struct
import sys

from serial import Serial
import pyaudio

class StreamServer(object):
    CHUNKSIZE = 1024
    RATE = 48000
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    #encoder = '/usr/bin/oggenc --raw --raw-bits=16 --raw-chan=%i --raw-rate=%i -' % (CHANNELS, RATE)
    #encoder = '/usr/local/bin/lame -r --bitwidth 16 -a -s %i - -' % RATE
    ENCODER = '/bin/cat'

    def __init__(self, bindaddr='0.0.0.0'):
        self.clients = {}
        self.enc = Popen(self.ENCODER.split(' '), stdin=PIPE, stdout=PIPE)

        p = pyaudio.PyAudio()
        self.audio = p.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=2,
                frames_per_buffer=self.CHUNKSIZE)

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 1)

    def stream_reader(self):
        while True:
            try:
                data = self.audio.read(self.CHUNKSIZE)
            except:
                continue
            self.enc.stdin.write(data)

    def stream_server(self):
        while True:
            data = self.enc.stdout.read(self.CHUNKSIZE)
            while data:
                bytes = self.sock.sendto(data, 0, ('224.0.1.20', 9200))
                data = data[bytes:]

    def start(self):
        t2 = Thread(target=self.stream_reader)
        t2.setDaemon(True)
        t2.start()

        t3 = Thread(target=self.stream_server)
        t3.setDaemon(True)
        t3.start()

class ControlServer(object):
    def __init__(self, device='/dev/ttyUSB0', baud=57600):
        self.serial = Serial(device, baud, timeout=1)
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
            readable = select(self.clients.keys(), [], [], 1)[0]
            for sock in readable:
                data = sock.recv(1024)
                if not data:
                    print 'Disconnected', self.clients[sock]
                    del self.clients[sock]
                    continue
                data = data.rstrip('\r\n')
                self.write(data)
            readable = select([self.serial], [], [], 1)[0]
            for serial in readable:
                self.buf += serial.read(1024)
                while self.buf.find('\r') != -1:
                    line, self.buf = self.buf.split('\r', 1)
                    for sock in self.clients.keys():
                        sock.send(line + '\n')

def main():
    streamer = StreamServer()
    streamer.start()
    control = ControlServer()

    t1 = Thread(target=control.accept_loop, args=[])
    t1.setDaemon(True)
    t1.start()

    control.run()

if __name__ == '__main__':
    main()
