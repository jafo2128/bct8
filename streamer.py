import pyaudio
from socket import socket
import sys

chunk = 1024
pa = pyaudio.PyAudio()

stream_info = pyaudio.PaMacCoreStreamInfo(flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice, channel_map=(0, 1))
stream = pa.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True,
                output_host_api_specific_stream_info=stream_info)

sock = socket()
sock.connect(('192.168.1.7', 9200))

while True:
    data = sock.recv(1024)
    stream.write(data)
    #sys.stdout.write(data)
