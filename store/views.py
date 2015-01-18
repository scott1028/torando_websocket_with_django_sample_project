import json
import time
from StringIO import StringIO

from django import http
from django.views.decorators.http import require_http_methods

import qrcode


@require_http_methods(["GET"])
def home(request):
    return http.HttpResponse(
        'request get  -> /store/:store_id/\n'
        '        qrcode decode -> [$random]$store_id[$random]\n'
        '\n'
        'request post -> /store/:store_id/check_in/\n'
        '        data -> {"store_id": "69678687687"}\n'
        '        resp -> {"uri_store_id": "1", "data_store_id": "2", "equal": false}\n',
        content_type='text/plain')

@require_http_methods(["POST"])
def store_id_check_in(request, store_id = False):
    try:
        assert request.META['CONTENT_TYPE'] == 'application/json'
        assert 'application/json' in request.META['CONTENT_TYPE'].lower()
        input_data = json.loads(request.body)
    except Exception:
        return http.HttpResponse(status=415)
    
    output_data = {}
    output_data['uri_store_id'] = store_id
    output_data['data_store_id'] = input_data.get('store_id', None)
    output_data['auth'] = (store_id == input_data.get('store_id', None))
    resp = http.HttpResponse(json.dumps(output_data), status=200)
    resp['Content-Type'] = 'application/json'
    resp['uri-store-id'] = store_id
    resp['data-store-id'] = input_data.get('store_id', None)
    return resp

@require_http_methods(["GET"])
def store_id(request, store_id):
    prefix_key = int(time.time()/10).__str__()
    message = '[%s]%s[%s]' % (prefix_key, store_id, prefix_key)

    img = qrcode.make(message)

    fd = StringIO()
    img.save(fd)

    resp = http.HttpResponse(fd.getvalue(), status=200)
    resp['Content-Type'] = 'image/png'
    resp['store-id'] = store_id
    fd.close()
    return resp




from socketio.namespace import BaseNamespace
from socketio import socketio_manage

class ChatNamespace(BaseNamespace):
    def on_chat(self, msg):
        self.emit('chat', msg)

def socketio_service(request):
    # request.environ.get('wsgi.input')
    # request.environ['socketio'] = request.environ.get('wsgi.input')
    socketio_manage(request.environ, {'/chat': ChatNamespace}, request)
    return http.HttpResponse("")
