import pyaudio
from socket import socket, SOCK_DGRAM
from subprocess import Popen, PIPE
from threading import Thread
import sys

chunk = 1024
pa = pyaudio.PyAudio()

stream_info = pyaudio.PaMacCoreStreamInfo(flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice, channel_map=(0, 1))
stream = pa.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True,
                output_host_api_specific_stream_info=stream_info)

sock = socket(SOCK_DGRAM)
sock.connect(('192.168.1.7', 9200))
#decoder = '/usr/local/bin/lame - -'
decoder = '/bin/cat'

#p = Popen(decoder.split(' '), stdin=PIPE, stdout=PIPE)

def read_stream():
    while True:
        data = sock.recv(1024)
        stream.write(data)
        #sys.stdout.write(data)
        #p.stdin.write(data)

def play_stream():
    while True:
        data = p.stdout.read()
        stream.write(data)

#t = Thread(target=read_stream)
#t.setDaemon(True)
#t.start()

#play_stream()
read_stream()
