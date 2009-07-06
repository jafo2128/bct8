from serial import Serial
from pprint import pprint
from threading import Thread
import sys

class BCT8(Thread):
    def __init__(self, device='/dev/ttyUSB0'):
        Thread.__init__(self)
        self.setDaemon(True)
        self.serial = Serial(device, 57600, timeout=1)
        self.handlers = []

    def run(self):
        buf = ''
        while True:
            buf += self.serial.read(512)
            while buf.find('\r') != -1:
                line, buf = buf.split('\r', 1)
                self.recv(line)

    def send(self, cmd):
        self.serial.write(cmd + '\r')

    def recv(self, line):
        sys.stdout.write(line + '\n')
    
    def get_mode(self):
        return self.sr('MD')

if __name__ == '__main__':
    radio = BCT8()
    radio.start()

    while True:
        sys.stdout.write('BCT8> ')
        line = sys.stdin.readline().rstrip('\r\n')
        radio.send(line)
