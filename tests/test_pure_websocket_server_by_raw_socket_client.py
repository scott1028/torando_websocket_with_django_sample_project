import time
from websocket import create_connection


ws = create_connection("ws://127.0.0.1:8888/")
print "Sending 'Hello, World'..."
ws.send("Hello, World")
print "Sent"
print "Reeiving..."

result =  ws.recv()
print "Received '%s'" % result

raw_input('press any key to exit.')
import pdb; pdb.set_trace()
ws.close()
