from serial import Serial
from pprint import pprint

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

fd = file('dump.dat', 'w')
for chan in xrange(1, 250):
    cmd = 'PM' + str(chan).rjust(3, '0')
    radio.write(cmd)

    line = ''
    while not line.startswith('C'):
        line = radio.readline()
    chan, freq, params = line.split(' ', 2)
    params = params.split(' ', 5)
    if params[0] == 'TF':
        trunk = ' '
    else:
        trunk = 'T'
    chan = chan.lstrip('C')
    #chan = int(chan.lstrip('C'))
    freq = freq.lstrip('F')
    #freq = int(freq[:4]) + (float(freq[4:]) / 1000.0)
    print 'PM%s%s%s' % (chan, trunk, freq)
    fd.write('PM%s%s%s\n' % (chan, trunk, freq))
fd.flush()
fd.close()
