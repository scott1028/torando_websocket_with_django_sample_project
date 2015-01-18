# coding: utf-8

import tornado.ioloop
import tornado.web
from tornado import websocket

# Intergate Django
import os
import sys
import json

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "queue_inline.settings")
django.setup()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        import datetime
        from store.models import Person
        from django.core import serializers

        from django.core.serializers.json import DjangoJSONEncoder

        # add new record
        from django.db import transaction
        with transaction.autocommit():
            Person(first_name='a', last_name='b', create_date=datetime.datetime.now()).save()

        # if you want to pass obj to another process then deserialize it!
        # data = serializers.serialize("json", Person.objects.all())

        # if you only want to return data, use DjangoJSONEncode 否則日期欄位那些會出現轉換錯誤
        data = json.dumps([row for row in Person.objects.all().values()], cls=DjangoJSONEncoder)

        # 第三種寫法
        # data = DjangoJSONEncoder().encode([ i for i in Person.objects.all().values()])

        self.set_header('Content-Type', 'application/json')
        self.write(data)


class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        from store.models import Person
        from django.core import serializers
        data = serializers.serialize("json", Person.objects.all())

        last_person = Person.objects.last()
        if last_person:
            last_person.delete()

        print 'Client Say:' + message
        self.write_message(data)

    def on_close(self):
        print "WebSocket closed"


application = tornado.web.Application([
    (r"/", MainHandler),
    (r'/ws/', EchoWebSocket),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'})
])

if __name__ == "__main__":
    # by tornado, websocket feature support
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

    # by wsgi, no websocket
    # import tornado.wsgi
    # import wsgiref.simple_server
    # wsgi_app = tornado.wsgi.WSGIAdapter(application)
    # server = wsgiref.simple_server.make_server('', 8888, wsgi_app)
    # server.serve_forever()
