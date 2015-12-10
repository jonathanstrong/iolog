from tornado.options import define, options
import tornado.web
import iolog.base


define('tcp_port', default=9020, type=int, help='port to listen for log events')
define('ws_port', default=-1, type=int, help='port to send websocket messages and serve page. If -1 will only print TCP messages to console.')
define('n_display_items', default=100, help='number of log events to keep displayed before purging oldest')

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('base.html', port=options.ws_port, n_display_items=options.n_display_items)

def make_app():
    return tornado.web.Application([
        (r'/$', MainHandler), 
        (r'/ws', iolog.base.WebSocketHandler),
    ])

if __name__ == '__main__':
    tornado.options.parse_command_line()
    tcp = iolog.base.TCPServer(ws=bool(options.ws_port != -1))
    tcp.listen(options.tcp_port)
    if options.ws_port != -1:
        app = make_app()
        app.listen(options.ws_port)
    tornado.ioloop.IOLoop.current().start()
