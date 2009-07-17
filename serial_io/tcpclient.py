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

sock = socket()
sock.connect(('127.0.0.1', 9201))

def read_stream():
    while True:
        #p.stdin.write(sock.recv(CHUNKSIZE))
        data = sock.recv(CHUNKSIZE)
        audio.write(data)
        #sys.stdout.write(data)
        #p.stdin.write(data)

read_stream()
