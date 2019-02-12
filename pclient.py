#!/usock./bin/env python
import socket
import hashlib
import random
import time
import sys
TCP_IP = '127.0.0.1'
TCP_PORT = 1878
BUFFER_SIZE = 1024
MESSAGE = "startplease"
time.sleep(5)
random.seed(1848)
data = ""
#sock.send(MESSAGE)
#data = sock.recv(BUFFER_SIZE)
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect((TCP_IP, TCP_PORT))
resp = sys.argv[1]
sanity = 0
while(data!="Yes" and sanity<30):
    time.sleep(1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    sock.send("canCommit?\31"+resp)
    data = sock.recv(BUFFER_SIZE)
    sanity = sanity+1
sanity = 0
while(data!="ACK" and sanity<30):
    time.sleep(1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    sock.send("preCommit\31" + resp)
    data = sock.recv(BUFFER_SIZE)
    sanity = sanity+1
    print "client received:", data
sanity = 0
while(data!="haveCommitted" and sanity<30):
    time.sleep(1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    sock.send("doCommit\31" + resp)
    data = sock.recv(BUFFER_SIZE)
    sanity = sanity+1
    print "client received:", data

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))
sock.send("doCommit\31" + resp)
data = sock.recv(BUFFER_SIZE)
print "client received:", data

sock.close()

