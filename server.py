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


# Collection All Connection
WS_CON_POOL = []


class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        print "WebSocket opened, 順便收集入連線池"

        # add con, ping-pong counter
        self.ping_counter = 0
        self.pong_counter = 0
        WS_CON_POOL.append(self)

    def on_pong(self, data):
        print data, 'Yes', self
        self.pong_counter += 1

    def on_connection_close(self):
        super(EchoWebSocket, self)
        print 'connection lose, 可能為對方當機或是我方關閉連線, 簡單來說 ping-pong 沒訊號了'
        WS_CON_POOL.remove(self)

    def on_message(self, message):
        print 'Total Online Connection->', len(WS_CON_POOL)

        from store.models import Person
        from django.core import serializers
        data = serializers.serialize("json", Person.objects.all())

        last_person = Person.objects.last()
        if last_person:
            last_person.delete()


        # 
        print 'Client Say:' + message
        self.write_message(data)
        self.write_message('test second message sent')
        self.write_message(str(WS_CON_POOL))
        # self.write_message('\x20', binary=True)


        # 
        print 'Boradcase to All'
        self.write_broadcast(message)

    def write_broadcast(self, message):
        for ws in WS_CON_POOL:
            print ws, ws.ping_counter, ws.pong_counter

            if ws.ping_counter - ws.pong_counter > 10:
                print '強至關閉無回應的客戶端->', ws
                ws.close()
                # on_connection_close, will remove it from WS_CON_POOL

            else:
                ws.write_message(json.dumps({
                    'namespace': 'broadcast',
                    'message': message
                }))

                # 若該連線已經死亡或當機了,
                # 就不會出現 on_pong Event,
                # 所以當 ping - pong 數字很大的時候可以考慮關閉該連線.
                # 
                # 當然也可以直接寫一個 Thread 來作 Ping-Pong 檢查.
                # 
                # 可以透過 tests/test_ws_sample_no_close.py, 來驗證
                ws.ping('test_if_connection_alive?')
                ws.ping_counter += 1

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
    server = tornado.ioloop.IOLoop.instance()
    # import datetime
    # def callback():
    #     print 123
    # server.add_timeout(datetime.timedelta(seconds=5), callback)
    server.start()

    # by wsgi, no websocket
    # import tornado.wsgi
    # import wsgiref.simple_server
    # wsgi_app = tornado.wsgi.WSGIAdapter(application)
    # server = wsgiref.simple_server.make_server('', 8888, wsgi_app)
    # server.serve_forever()
