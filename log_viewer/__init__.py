import tornado.ioloop
import tornado.web
import tornado.tcpserver
import tornado.websocket
import cPickle as pickle
import struct
import logging
import time
import StringIO

#log_format = '[%(time_since_last_any)s][%(asctime)s][%(levelname)s][%(filename)s:%(funcName)s:%(lineno)s] %(message)s'
log_format = '[%(asctime)s][%(levelname)s][%(filename)s:%(funcName)s:%(lineno)s] %(message)s'

ws = None

class TCP(tornado.tcpserver.TCPServer):
    def __init__(self, *args, **kwargs):
        super(TCP, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.buffer = StringIO.StringIO()
        self.log_handler = logging.StreamHandler(self.buffer)
        self.log_format = logging.Formatter(log_format)
        self.log_handler.setFormatter(self.log_format)
        self.logger.addHandler(self.log_handler)
        

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

        record = logging.makeLogRecord(self.unpickle(self.data))
        self.handle_log_record(record)
        self.slen = None
        self.data = ''
        self._stream.read_bytes(4, self._first)

    def unpickle(self, data):
        return pickle.loads(data)

    def handle_log_record(self, record):
        """
        we "handle" the log record, sending it to our StringIO
        buffer, which we pass on to the websocket and then erase
        from buffer.
        """
        self.logger.handle(record)
        record = self.buffer.getvalue()
        self.buffer.truncate(0)
        if ws:
            ws.write_message(record)
        else: 
            print 'ws is None, record not sent: {}'.format(record)



class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        if ws is None:
            print 'setting {} to global ws'.format(self)
            ws = self

    def open(self, *args):
        print "New connection"
        self.write_message("Welcome!")

    def on_message(self, message):
        print 'websocket received this: {}'.format(message)
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
