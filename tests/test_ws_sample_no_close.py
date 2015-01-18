import time
from websocket import create_connection


clients = []

for i in xrange(10):
    ws = create_connection("ws://127.0.0.1:8888/ws/")
    print "Sending 'Hello, World'..."
    ws.send("Hello, World")
    print "Sent"
    print "Reeiving..."

    result =  ws.recv()
    print "Received '%s'" % result
    result =  ws.recv()
    print "Received '%s'" % result
    result =  ws.recv()
    print "Received '%s'" % result
    result =  ws.recv()
    print "Received '%s'" % result
    clients.append(ws)

raw_input('press any key to exit.')
for ws in clients:
    ws.close()
