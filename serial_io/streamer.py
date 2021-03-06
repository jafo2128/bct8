from subprocess import Popen, PIPE
from threading import Thread
from socket import *
from time import clock
import aifc
import struct
import sys

import pyaudio

CHUNKSIZE = 1024
pa = pyaudio.PyAudio()

stream_info = pyaudio.PaMacCoreStreamInfo(flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice, channel_map=(0, 1))
audio = pa.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True,
                output_host_api_specific_stream_info=stream_info)

sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
sock.bind(('', 9200))
mreq = struct.pack('4sl', inet_aton('224.0.1.20'), INADDR_ANY)
sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

#decoder = '/usr/local/bin/lame --decode - -'
decoder = '/bin/cat'

p = Popen(decoder.split(' '), stdin=PIPE, stdout=PIPE)

def read_stream():
    while True:
        #p.stdin.write(sock.recv(CHUNKSIZE))
        data = sock.recv(CHUNKSIZE)
        audio.write(data)
        #sys.stdout.write(data)
        #p.stdin.write(data)

def play_stream():
    while True:
        audio.write(p.stdout.read(CHUNKSIZE))

#t = Thread(target=read_stream)
#t.setDaemon(True)
#t.start()

read_stream()

#t1 = Thread(target=play_stream)
#t1.setDaemon(True)
#t1.start()

