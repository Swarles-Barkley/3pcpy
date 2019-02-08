#!/usock./bin/env python
import socket
import hashlib
import random
import time
TCP_IP = '127.0.0.1'
TCP_PORT = 1878
BUFFER_SIZE = 1024
MESSAGE = "startplease"
time.sleep(10)
random.seed(1848)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))
#sock.send(MESSAGE)
#data = sock.recv(BUFFER_SIZE)
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((TCP_IP, TCP_PORT))
resp = "ZOOPZOOP!"
sock.send("canCommit?\31"+resp)
data = sock.recv(BUFFER_SIZE)
print "client received:", data

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))
#sock.connect((TCP_IP, TCP_PORT))
sock.send("preCommit\31" + resp)
data = sock.recv(BUFFER_SIZE)
print "client received:", data

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))
sock.send("doCommit\31" + resp)
data = sock.recv(BUFFER_SIZE)
print "client received:", data

sock.close()

