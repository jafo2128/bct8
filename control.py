from socket import socket

def encode_freq(freq):
    major, minor = str(freq).split('.', 1)
    s = major.rjust(4, '0')
    s += minor.ljust(4, '0')
    return s

def decode_freq(freq):
    freq = freq.lstrip('F')
    major = float(freq[:4])
    minor = float(freq[4:])
    minor *= 0.0001
    return major + minor

class RadioControl(object):
    def __init__(self, server):
        self.server = server
        self.sock = socket()
        self.sock.connect(server)
        self.buf = ''

    def send(self, cmd):
        print '>', cmd
        cmd += '\n'
        while cmd:
            bytes = self.sock.send(cmd)
            cmd = cmd[bytes:]
        return self.readline()

    def readline(self):
        while self.buf.find('\n') == -1:
            print 'loop', repr(self.buf)
            self.buf += self.sock.recv(1024)

        line, self.buf = self.buf.split('\n', 1)
        print '<', line
        return line

    def set_frequency(self, freq):
        if self.send('RF' + encode_freq(freq)) != 'OK':
            return False
        else:
            return True

    def dump_memory(self, bank):
        dump = []
        for i in range(1, 50):
            num = (bank * 50) + i
            value = self.send('PM%03i' % num)
            dump.append(decode_freq(value.split(' ')[1]))
        return dump

    def load_memory(self, bank, dump, trunk=False):
        count = 0
        for freq in dump:
            count += 1
            if trunk:
                trunk = 'T'
            else:
                trunk = ' '
            cmd = 'PM%03i%s%s' % (count, trunk, encode_freq(freq))
            self.send(cmd)

def test():
    control = RadioControl(('192.168.1.7', 9200))
    dump = control.dump_memory(0)
    print repr(dump)
    control.load_memory(0, dump)

if __name__ == '__main__':
    test()
