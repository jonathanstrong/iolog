import tornado.ioloop
import tornado.web
import tornado.tcpserver
import tornado.websocket
import cPickle as pickle
import struct
import logging
import time

class TCP(tornado.tcpserver.TCPServer):
    #def __init__(self, ws, *args, **kwargs):
    #    self.ws = ws
    #    super(TCP, self).__init__(*args, **kwargs)

    def handle_stream(self, stream, address):
        self._stream = stream
        self.slen = None
        self.data = ''
        print 'handle stream {}'.format(stream)
        self._stream.read_bytes(4, self._first)

    def _first(self, chunk):
        if len(chunk) >= 4: 
            self.slen = struct.unpack(">L", chunk)[0]
            self._stream.read_bytes(self.slen-len(self.data), self._read)
        else:
            self._stream.read_bytes(4, self._first)

    def _read(self, chunk):
        self.data += chunk
        if len(self.data) == self.slen:
            self._process()
        else: 
            self._stream.read_bytes(self.slen-len(self.data), self._read)

    def _process(self):
        #print self.data

        obj = logging.makeLogRecord(pickle.loads(self.data))
        print time.time(), obj
        self.slen = None
        self.data = ''
        self._stream.read_bytes(4, self._first)

    def unpickle(self, data):
        return pickle.loads(data)

    def handle_log_record(self, record):
        print record


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print "New connection"
        self.write_message("Welcome!")

    def on_message(self, message):
        self.write_message(message)

    def on_close(self):
        print "Connection closed"

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('base.html')

def make_app():
    return tornado.web.Application([
        (r'/$', MainHandler), 
        (r'/ws/?', WebSocketHandler),
    ])

if __name__ == '__main__':
    tcp = TCP()
    tcp.listen(7070)
    app = make_app()
    app.listen(6060)
    tornado.ioloop.IOLoop.current().start()
