from flup.server.fcgi import WSGIServer
from daemon import become_daemon
from threading import Thread
from webob import Request
from socket import socket
from select import select
from Queue import Queue
import re

class LiveHTTPStreamer(object):
    def __init__(self):
        self.urls = [
            ('^/scanner/stream.m3u8$', self.index),
            ('^/scanner/stream.ts$', self.stream),
        ]
        self.urls = [(re.compile(pattern), func) for pattern, func in self.urls]
        self.queues = []

    def __call__(self, environ, start_response):
        request = Request(environ)
        
        for pattern, func in self.urls:
            match = pattern.match(request.path_info)
            if match:
                return func(start_response, request, match)
        return self.redirect(start_response, request, match)

    def redirect(self, start_response, request, match):
        start_response('302 Found', [('Location', 'http://neohippie.net/scanner/stream.m3u8')])
        return ['']

    def index(self, start_response, request, match):
        start_response('200 OK', [('Content-type', 'application/x-mpegURL')])
        return ['''#EXTM3U
#EXTINF:10,
http://neohippie.net/scanner/stream.ts
#EXT-X-ENDLIST''']

    def stream(self, start_response, request, match):
        start_response('200 OK', [('Content-type', 'video/MP2T')])
        q = Queue()
        self.queues.append(q)
        print 'Starting output stream for', request.remote_addr
        while True:
            try:
                yield q.get()
            except:
                if q in self.queues:
                    self.queues.remove(q)
                    print 'No longer sending data to', request.remote_addr
                return

def input_loop(app):
    sock = socket()
    sock.bind(('', 9201))
    sock.listen(1)
    while True:
        print 'Waiting for input stream'
        sd, addr = sock.accept()
        print 'Connected input stream from', addr
        data = True
        while data:
            readable = select([sd], [], [], 0.1)[0]
            for s in readable:
                data = s.recv(1024)
                if not data:
                    break
                for q in app.queues:
                    q.put(data)
        print 'Lost input stream from', addr
    
 
if __name__ == '__main__':
    app = LiveHTTPStreamer()
    #server = make_server('', 9200, app)
    server = WSGIServer(app, bindAddress=('', 9200))

    t1 = Thread(target=input_loop, args=[app])
    t1.setDaemon(True)
    t1.start()

    #become_daemon(out_log='http.out', err_log='http.err')
    server.run()
