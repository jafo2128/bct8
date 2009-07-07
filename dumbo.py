from subprocess import Popen, PIPE
from traceback import format_exc
from threading import Thread
from select import select
import struct
import socket
import sys

from serial import Serial
import pyaudio

MSG_AUDIO = 1
MSG_CONTROL = 2

class DumboMessage(object):
    def __init__(self, datatype=None, data=''):
        self.datatype = datatype
        self.data = data
        self.size = len(data)

    def send(self, sock):
        header = struct.pack('>HI', self.datatype, len(self.data))
        packet = header + self.data
        while len(packet) > 0:
            sentbytes = sock.send(packet)
            packet = packet[sentbytes:]

    def recv(self, sock):
        packet = sock.recv(1024)
        header = packet[:6]
        self.data = packet[6:]
        self.datatype, self.size = struct.unpack('>HI', header)
        while len(self.data) < self.size:
            self.data += sock.recv(self.size - len(self.data))

class StreamServer(object):
    CHUNKSIZE = 1024
    RATE = 48000
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    #encoder = '/usr/bin/oggenc --raw --raw-bits=16 --raw-chan=%i --raw-rate=%i -' % (CHANNELS, RATE)
    #encoder = '/usr/local/bin/lame -r --bitwidth 16 -a -s %i - -' % RATE
    ENCODER = '/bin/cat'

    def __init__(self, bindaddr='0.0.0.0', bindport=9200):
        self.clients = {}
        self.enc = Popen(self.ENCODER.split(' '), stdin=PIPE, stdout=PIPE)

        p = pyaudio.PyAudio()
        self.audio = p.open(format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=2,
                frames_per_buffer=self.CHUNKSIZE)

        self.server_sock = socket.socket(socket.SOCK_DGRAM)
        self.server_sock.bind((bindaddr, bindport))
        self.server_sock.listen(10)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def accept_loop(self):
        while True:
            client_sock, client_addr = self.server_sock.accept()
            self.clients[client_sock] = client_addr
            print 'Accepted connection from', client_addr

    def stream_reader(self):
        while True:
            try:
                data = self.audio.read(self.CHUNKSIZE)
            except:
                continue
            self.enc.stdin.write(data)

    def stream_server(self):
        dead = []
        while True:
            data = self.enc.stdout.read(self.CHUNKSIZE)
            msg = DumboMessage(MSG_AUDIO, data)
            for client_sock in self.clients:
                try:
                    msg.send(client_sock)
                except socket.error:
                    dead.append(client_sock)
                except:
                    print format_exc()
                    dead.append(client_sock)
            for d in dead:
                if d in self.clients:
                    print 'Disconnected', self.clients[d]
                    del self.clients[d]

    def start(self):
        t1 = Thread(target=self.accept_loop)
        t1.setDaemon(True)
        t1.start()

        t2 = Thread(target=self.stream_reader)
        t2.setDaemon(True)
        t2.start()

        t3 = Thread(target=self.stream_server)
        t3.setDaemon(True)
        t3.start()

class ControlServer(object):
    def __init__(self, device='/dev/ttyUSB0', baud=57600):
        self.serial = Serial(device, baud, timeout=1)
        self.handlers = []
        self.buf = ''

    def readlines(self, bufsize=512):
        while True:
            self.buf += self.serial.read(bufsize)
            while self.buf.find('\r') != -1:
                line, self.buf = self.buf.split('\r', 1)
                yield line

    def write(self, cmd):
        self.serial.write(cmd + '\r')

def main():
    streamer = StreamServer()
    streamer.start()
    control = ControlServer()

    for line in control.readlines():
        msg = DumboMessage(MSG_CONTROL, line)
        for client in streamer.clients.keys():
            msg.send(client)

        readable = select(streamer.clients.keys(), timeout=0)[0]
        for client in readable:
            msg = DumboMessage()
            msg.recv(client)
            if msg.datatype == MSG_CONTROL:
                control.write(msg.data)
            else:
                print 'Recieved non-control message from', streamer.clients[client]

if __name__ == '__main__':
    main()
