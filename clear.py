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
        print cmd
        self.serial.write(cmd + '\r')

radio = BCT8()

for chan in xrange(1, 50):
    chan = str(chan).rjust(3, '0')
    radio.write('PM%s 00000000\r' % chan)
    print radio.readline()
    sleep(0.02)
