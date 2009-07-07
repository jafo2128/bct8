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

class DumboTransport(object):
    def __init__(self, sock):
        self.sock = sock

    def send(self, msg):
        if msg.datatype != MSG_AUDIO: print '>', msg
        packet = msg.encode()
        while packet:
            sentbytes = self.sock.send(packet)
            packet = packet[sentbytes:]

    def recv(self):
        packet = self.sock.recv(1024)
        while packet:
            datatype, datasize = struct.unpack('>HI', packet[:6])
            packet = packet[:6]
            while len(packet) < datasize:
                packet += self.sock.recv(datasize - len(packet))
            msg = DumboMessage(datatype, packet)
            if msg.datatype != MSG_AUDIO: print '>', msg
            yield msg
        return

    def __str__(self):
        return repr(self.sock.getpeername())

class DumboMessage(object):
    def __init__(self, datatype=None, data=''):
        self.datatype = datatype
        self.data = data
        self.size = len(data)

    def encode(self):
        header = struct.pack('>HI', self.datatype, len(self.data))
        return header + self.data

    def __str__(self):
        if self.datatype == MSG_CONTROL:
            return '(control) %s' % repr(self.data)
        if self.datatype == MSG_AUDIO:
            return '(audio) %i' % len(self.data)
        return '(unknown) %s' % repr(self.data)

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

        self.server_sock = socket.socket()
        self.server_sock.bind((bindaddr, bindport))
        self.server_sock.listen(10)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def accept_loop(self):
        while True:
            client_sock, client_addr = self.server_sock.accept()
            self.clients[DumboTransport(client_sock)] = client_addr
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
                    client_sock.send(msg)
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

def bcast_control(control, streamer):
    for line in control.readlines():
        msg = DumboMessage(MSG_CONTROL, line)
        for client in streamer.clients.keys():
            client.send(msg)
    
def main():
    streamer = StreamServer()
    streamer.start()
    control = ControlServer()

    t1 = Thread(target=bcast_control, args=[control, streamer])
    t1.setDaemon(True)
    t1.start()

    while True:
        mapping = streamer.clients.keys()
        mapping = dict(zip([x.sock for x in mapping], mapping))
        readable = select([x.sock for x in streamer.clients.keys()], [], [], 1)[0]
        for client in readable:
            client = mapping[client]
            print 'got data from', client
            for msg in client.recv():
                if msg.datatype == MSG_CONTROL:
                    control.write(msg.data)
                else:
                    print 'Recieved non-control message from', streamer.clients[client]

if __name__ == '__main__':
    main()
