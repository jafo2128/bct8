from dumbo import DumboTransport, MSG_AUDIO, MSG_CONTROL
from socket import socket
from select import select
import pyaudio
import sys

def main():
    pa = pyaudio.PyAudio()
    stream_info = pyaudio.PaMacCoreStreamInfo(flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice, channel_map=(0, 1))
    audio = pa.open(format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True,
                output_host_api_specific_stream_info=stream_info)

    sock = socket()
    sock.connect(('127.0.0.1', 9200))
    transport = DumboTransport(sock)

    while True:
        readable = select([sys.stdin], [], [], 0)[0]
        if readable:
            line = sys.stdin.readline().rstrip('\r\n')
            msg = DumboMessage(MSG_CONTROL, line)
            msg.send(sock)

        for msg in transport.recv():
            if msg.datatype == MSG_AUDIO:
                audio.write(msg.data)
                continue
            if msg.datatype == MSG_CONTROL:
                print msg.data

if __name__ == '__main__':
    main()
