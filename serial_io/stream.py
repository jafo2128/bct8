import socket
from threading import Thread
from traceback import format_exc
from subprocess import Popen, PIPE
import pyaudio
#from pylab import *
import struct
import array

chunk = 1024
RATE = 48000
CHANNELS = 1
FORMAT = pyaudio.paInt16
#encoder = '/usr/bin/oggenc --raw --raw-bits=16 --raw-chan=%i --raw-rate=%i -' % (CHANNELS, RATE)
#encoder = '/usr/local/bin/lame -r --bitwidth 16 -a -s %i - -' % RATE
encoder = '/bin/cat'

def accept_loop(sd):
    while True:
        sock = sd.accept()
        clients.append(sock)
        print 'Accepted connection from', sock[1]

def feeder(enc):
    while True:
        try:
            data = stream.read(chunk)
        except:
            continue
        enc.stdin.write(data)

def stream_server(enc, clients):
    dead = []
    while True:
        data = enc.stdout.read(1024)
        for c in clients:
            client_sock, client_addr = c
            try:
                client_sock.send(data)
            except socket.error:
                dead.append(c)
            except:
                print format_exc()
                dead.append(c)
        for d in dead:
            if d in clients:
                print 'Disconnected', d[1]
                clients.remove(d)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=2,
                frames_per_buffer=chunk)

sock = socket.socket(socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 9200))
sock.listen(10)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

clients = []

print 'Starting encoder...'
enc = Popen(encoder.split(' '), stdin=PIPE, stdout=PIPE)

print 'Starting accept loop...'
t1 = Thread(target=accept_loop, args=[sock])
t1.setDaemon(True)
t1.start()

print 'Starting input feeder...'
t2 = Thread(target=feeder, args=[enc])
t2.setDaemon(True)
t2.start()

print 'Starting stream server...'
stream_server(enc, clients)
