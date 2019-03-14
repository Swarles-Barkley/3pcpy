#!/usr/bin/env python

# pnode is an embedded node in the network,
# and a node in the three phase commit protocol

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
PORT_START = 32400
BUFFER_SIZE = 1024
#time.sleep(5)
random.seed(1848)

nodenum = int(sys.argv[1])
N = int(sys.argv[2])
random.seed(1848 + nodenum)

MY_PORT = PORT_START + nodenum

done = threading.Event()

data_lock = threading.Lock() # protects variables below
state = ""

stats_lock = threading.Lock()
sent_bytes = 0
received_bytes = 0

def log(*args):
    print("[client %s]" % nodenum, *args)

# each node keeps track of its connection quality to the coordinator nodes in the cluster
neighbors = [
    # node, quality
    (0, random.random()),
    (1, random.random()),
    (2, random.random()),
]

nodedata = {
    "port": MY_PORT,
    "nbr": neighbors,
}

class Timeout(Exception):
    """Request timed out"""

def send(msg):
    global sent_bytes
    global received_bytes
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_IP, TCP_PORT))
    try:
        sock.send(msg)
        with stats_lock:
            sent_bytes += len(msg)
        data = sock.recv(BUFFER_SIZE)
        with stats_lock:
            received_bytes += len(data)
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
    global received_bytes
    def reply(msg):
        global sent_bytes
        r = conn.send(msg)
        with stats_lock:
            sent_bytes += len(msg)
        return r
    try:
        data = conn.recv(BUFFER_SIZE)
        with stats_lock:
            received_bytes += len(data)
        if not data: return
        log("data is ", data)
        cmd = data

        if cmd == "canCommit?":
            with data_lock:
                state = "waiting"
                #candidate = extra[0]
            reply("Yes")

        elif cmd=="preCommit":
            with data_lock:
                state = "precommit"
            reply("ACK")

        elif cmd == "doAbort":
            with data_lock:
                state = "aborted"
            reply("haveAborted")
            done.set()

        elif cmd=="doCommit":
            with data_lock:
                state = "committed"
            reply("haveCommitted")
            done.set()

        else:
            log("don't understand:", data)
    finally:
        conn.close()

def recovery():
    # elect new coordinator ????
    # coordinator colects states
    # decision:
    #   any aborted -> abort
    #   any committed -> commit
    #   any pre-committed, and a quorum of sites are in wit or precommit -> precommit
    #   a quorum of sites in wait or pre-abort -> preabort
    #   otherwise -> block
    # send decision to all nodes
    # nodes respond

    # DISREGARD

    # 1. unilaterally abort, then call a new election
    pass

def serverthread(sock):
    while 1:
        conn, addr = sock.accept()
        thr = threading.Thread(target=threadConn, args=(conn,))
        thr.start()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((TCP_IP, MY_PORT))
    sock.listen(5)

    data = trysend("hello\37"+str(nodenum)+"\37" + json.dumps(nodedata))
    log("sent hello, received:", data)

    thr = threading.Thread(target=serverthread, args=(sock,))
    thr.daemon = True
    thr.start()

    done.wait()

    log("final state:", state)
    with stats_lock:
        log("sent %d bytes" % sent_bytes)
        log("received %d bytes" % received_bytes)

main()
