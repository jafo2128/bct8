from serial import Serial
from pprint import pprint
from time import sleep
import sys

class BCT8(object):
    def __init__(self, device='/dev/ttyUSB0'):
        self.serial = Serial('/dev/ttyUSB0', 57600, timeout=0.02)
        self.buf = ''

    def readline(self, bufsize=512):
        while True:
            self.buf += self.serial.read(512)
            while self.buf.find('\r') != -1:
                line, self.buf = self.buf.split('\r', 1)
                return line

    def write(self, cmd):
        self.serial.write(cmd + '\r')

radio = BCT8()

for line in file(sys.argv[1], 'r'):
    line = line.rstrip('\r\n') + '\r'
    print repr(line)
    radio.write(line)
    line = ''
    while not line.startswith('C'):
        line = radio.readline()
        print repr(line)
    sleep(0.02)
