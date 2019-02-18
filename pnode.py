#!/usr/bin/env python

# pnode is a node in the three phase commit protocol

from __future__ import print_function
import hashlib
import json
import random
import socket
import sys
import threading
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 3878
BUFFER_SIZE = 1024
#time.sleep(5)
random.seed(1848)

nodenum = int(sys.argv[1])
N = int(sys.argv[2])

MY_PORT = TCP_PORT + nodenum + 1

data_lock = threading.Lock() # protects variables below
state = ""

def log(*args):
    print("[client %s]" % nodenum, *args)

neighbors = [
    # node, quality
    (0, 0.1),
    (1, 0.5),
    (2, 0.7),
]

nodedata = {
    "port": MY_PORT,
    "nbr": neighbors,
}

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

def threadConn(conn):
    global state
    data = conn.recv(BUFFER_SIZE)
    if not data: return
    log("data is ", data)
    cmd = data

    if cmd == "canCommit?":
        with data_lock:
            state = "waiting"
            #candidate = extra[0]
        conn.send("Yes")

    elif cmd=="preCommit":
        with data_lock:
            pass
        conn.send("ACK")

    elif cmd=="doCommit":
        with data_lock:
            pass
        conn.send("haveCommitted")

    else:
        log("don't understand:", data)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, MY_PORT))
    sock.listen(5)

    data = trysend("hello\31"+str(nodenum)+"\31" + json.dumps(nodedata))
    log("sent hello, received:", data)

    while 1:
        conn, addr = sock.accept()
        thr = threading.Thread(target=threadConn, args=(conn,))
        thr.start()
        #conn.send(data)

    #data = trysend("canCommit?\31"+nodenum)

    #data = trysend("preCommit\31" + nodenum)
    #log("received:", data)

    #data = trysend("doCommit\31" + nodenum)
    #log("received:", data)

main()
