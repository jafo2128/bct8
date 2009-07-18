from socket import socket

def encode_freq(freq):
    major, minor = str(freq).split('.', 1)
    s = major.rjust(4, '0')
    s += minor.ljust(4, '0')
    return s

def decode_freq(freq):
    freq = freq.lstrip('F')
    major = int(freq[:4])
    minor = int(freq[4:])
    return '%i.%i' % (major, minor)

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
            self.buf += self.sock.recv(1024)

        line, self.buf = self.buf.split('\n', 1)
        print '<', line
        return line

    def set_frequency(self, freq):
        if self.send('RF' + encode_freq(freq)) == 'OK':
            return True
        else:
            return False

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

    def set_boolean(self, cmd, flag):
        if flag:
            flag = 'N'
        else:
            flag = 'F'
        if self.send(cmd + flag) == 'OK':
            return True
        else:
            return False

    def set_status_bit(self, flag):
        return self.set_boolean('BT', flag)

    def set_delay(self, flag):
        return self.set_boolean('DL', flag)

    def set_data_skip(self, flag):
        return self.set_boolean('DS', flag)

    def set_enter_lock(self, flag):
        return self.set_boolean('EL', flag)

def test():
    control = RadioControl(('192.168.1.7', 9200))
    dump = control.dump_memory(0)
    control.load_memory(0, dump)
    assert control.set_frequency('121.5')

if __name__ == '__main__':
    test()
