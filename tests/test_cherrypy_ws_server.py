# coding: utf-8

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import EchoWebSocket, WebSocket

cherrypy.config.update({'server.socket_port': 8888})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()


# such as EchoWebSocket
class MyWebSocketProcessor(WebSocket):
    pass


class Root(object):
    @cherrypy.expose
    def index(self):
        return 'some HTML with a websocket javascript connection'

    @cherrypy.expose
    def test_ws(self):
        fd = open('../static/index.html')
        tpl = fd.read()
        fd.close()
        print tpl
        return tpl

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def test_json(self):
        import json
        return json.dumps([{'a': 1, 'b': 2}])

    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler

cherrypy.quickstart(Root(),
    '/',
    config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': EchoWebSocket
        }
    })
