#!/usr/bin/env python
from __future__ import print_function
import socket
import hashlib
import random
import time
import sys

TCP_IP = '127.0.0.1'
TCP_PORT = 1878
BUFFER_SIZE = 1024
#time.sleep(5)
random.seed(1848)
data = ""

resp = sys.argv[1]

def log(*args):
    print("[client %s]" % resp, *args)

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
    log("received:", data)
sanity = 0
while(data!="haveCommitted" and sanity<30):
    time.sleep(1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    sock.send("doCommit\31" + resp)
    data = sock.recv(BUFFER_SIZE)
    sanity = sanity+1
    log("received:", data)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))
sock.send("doCommit\31" + resp)
data = sock.recv(BUFFER_SIZE)
log("received:", data)

sock.close()

