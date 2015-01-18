from socketio.namespace import BaseNamespace

class ChatNamespace(BaseNamespace):
    def on_chat(self, msg):
        self.emit('chat', msg)

def socketio_service(request):
    socketio_manage(request.environ, {'/chat': ChatNamespace},
                    request)
    return "out"
