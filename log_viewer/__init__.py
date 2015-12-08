import tornado.ioloop
import tornado.web
import tornado.tcpserver
import tornado.websocket
import cPickle as pickle

class TCP(tornado.tcpserver.TCPServer):
    #def __init__(self, ws, *args, **kwargs):
    #    self.ws = ws
    #    super(TCP, self).__init__(*args, **kwargs)

    def handle_stream(self, stream, address):
        print stream
        self._stream = stream
        self._read_line()

    def _read_line(self):
        self._stream.read_until('\n', self._handle_read)

    def _handle_read(self, data):
        try:
            #converted = pickle.loads(data)
            pass
            #print data
        except Exception as e: 
            print '{}: {}'.format(type(e).__name__, e)
        #print 'data: {}'.format(pickle.loads(data))
        self._stream.write(data)
        self._read_line()

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
