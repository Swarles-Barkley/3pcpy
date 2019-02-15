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

nodenum = sys.argv[1]

def log(*args):
    print("[client %s]" % nodenum, *args)

class Timeout(Exception):
    """Request timed out"""

def send(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    try:
        sock.send(msg)
        data = sock.recv(BUFFER_SIZE)
        return data
    finally:
        sock.close()

def trysend(msg):
    for sanity in range(30):
        data = send(msg)
        if data and data != "Wait":
            return data
        time.sleep(1)

    raise Timeout()

def main():
    data = trysend("hello\31"+nodenum)

    data = trysend("canCommit?\31"+nodenum)

    data = trysend("preCommit\31" + nodenum)
    log("received:", data)

    data = trysend("doCommit\31" + nodenum)
    log("received:", data)

main()
