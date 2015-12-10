import tornado.ioloop
import tornado.web
import tornado.tcpserver
import tornado.websocket
import cPickle as pickle
import struct
import logging
import time
import StringIO


log_format = '[%(time_since_last_any)s][%(asctime)s][%(levelname)s][%(filename)s:%(funcName)s:%(lineno)s] %(message)s'
#log_format = '[%(asctime)s][%(levelname)s][%(filename)s:%(funcName)s:%(lineno)s] %(message)s'

websockets = [] 

class TCPServer(tornado.tcpserver.TCPServer):
    """
    we take the log records via TCP and send them
    to each open websocket connection. 

    this can also just print log records received
    via TCP if desired. 

    """
    ws = True # default flag for whether to route to websockets

    def __init__(self, *args, **kwargs):
        ws = kwargs.pop('ws', None)
        if ws:
            self.ws = ws
        super(TCPServer, self).__init__(*args, **kwargs)
        if self.ws:
            assert 'websockets' in globals(), 'Need an empty list "websockets" in global \
                    namespace to keep track of open connections.'
            self.logger = logging.getLogger(__name__)
            self.buffer = StringIO.StringIO()
            self.log_handler = logging.StreamHandler(self.buffer)
            self.log_format = logging.Formatter(log_format)
            self.log_handler.setFormatter(self.log_format)
            self.logger.addHandler(self.log_handler)
            self.logger.propagate = False
        else:
            "for just printing output"
            self.logger = logging.getLogger(__name__)
            self.log_format = logging.Formatter(log_format)
            self.log_handler = logging.StreamHandler()
            self.log_handler.setLevel(logging.DEBUG)
            self.log_handler.setFormatter(self.log_format)
            self.logger.addHandler(self.log_handler)
            self.logger.propagate = False

    def handle_stream(self, stream, address):
        self._stream = stream
        self.slen = None
        self.data = ''
        print 'handling stream {}'.format(stream)
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
        if self.ws:
            record = self.buffer.getvalue()
            self.buffer.truncate(0)
            for ws in websockets:
                ws.write_message(record)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        assert 'websockets' in globals(), 'Need an empty list "websockets" in global \
                namespace to keep track of open connections.'
        print "New connection"
        if self not in websockets:
            websockets.append(self)
        self.write_message("web socket connected")

    def on_message(self, message):
        #print 'websocket received this: {}'.format(message)
        self.write_message(message)

    def on_close(self):
        websockets.remove(self)
        print "Connection closed"

    def check_origin(self, origin):
        return True


