import logging
import tornado.websocket
import tornado.web
from tornado.web import url
import tornado.template
import websocket


logger = None


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print "New connection"
        self.write_message("Welcome!")

    def on_message(self, message):
        print '[ws debug] {}'.format(message)
        self.write_message(message)

    def on_close(self):
        print "Connection closed"

class WebSocketLogHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.ws = websocket.WebSocket()
        self.ws.connect('ws://localhost:6060/ws/')
        super(WebSocketLogHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        self.ws.send(record.message)

class MainHandler(tornado.web.RequestHandler):
    template = tornado.template.Template('''
        <html>
        <body>
        <script>
            var ws = new WebSocket('ws://localhost:6060/ws/');
            ws.onmessage = function(e) {
                console.log(e);
            }
        </script>
        </body>
        </html>
    ''')
    def get(self):
        global logger
        if logger is None:
            logger = get_logger()
        logger.debug('MainHandler.get')
        self.write(self.template.generate())

def make_app():
    return tornado.web.Application([
        url(r'/$', MainHandler), 
        url(r'/ws/?', WebSocketHandler, name='ws'),
    ])

#def tornado_log_fn(record):
#    logger.handle(record)

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = WebSocketLogHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

'''
settings = {
    'log_function': tornado_log_fn,
}
'''


if __name__ == '__main__':

    app = make_app()
    app.listen(6060)
    tornado.ioloop.IOLoop.current().start()



