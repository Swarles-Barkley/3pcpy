#!/usr/bin/env python

# pcoord is a coordinator in the three phase commit protocol

from __future__ import print_function
import hashlib
import json
import operator
import random
import socket
import sys
import threading
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 3878
BUFFER_SIZE = 1024
N = 3 # number of nodes
TIMEOUT = 0.250

data_lock = threading.Lock() # protects the following variables
nodes = {}
neighbors = {}

event = threading.Event()

def threadConn(conn):
    try:
        data = conn.recv(BUFFER_SIZE)
        if not data: return
        if '\37' not in data: return
        args = data.split('\37', 2)
        cmd = args[0]
        nodenum = int(args[1])
        extra = args[2:]
        print("data is", data)

        if cmd == "hello":
            nodedata = json.loads(extra[0])
            with data_lock:
                nodes[nodenum] = nodedata
                neighbors[nodenum] = nodedata['nbr']
                conn.send("ok")

                if len(nodes) >= N:
                    event.set()

        elif cmd == "startVote":
            with data_lock:
                candidate = nodenum
                conn.send("OK")
                # XXX inform other nodes about the vote...

        else:
            print("Server doesnt understand: " + data)
    finally:
        conn.close()

def send(nodenum, msg):
    with data_lock:
        port = nodes[nodenum]["port"]
    addr = (TCP_IP, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.settimeout(TIMEOUT)
    try:
        sock.send(msg)
        data = sock.recv(BUFFER_SIZE)
        return data
    except socket.timeout:
        return "Timeout"
    except socket.error:
        return "Error"
    finally:
        sock.close()

def run_the_protocol():
    canCommits = [False]*N
    preCommits = [False]*N
    doCommits = [False]*N
    with data_lock:
        winner = select_best_node(neighbors)
    print("electing node %s" % winner)


    with data_lock:
        xnodes = nodes.copy()

    # PHASE 1
    # TODO: send requests in parallel
    for n in xnodes:
        resp = send(n, "canCommit?")
        if resp == "Yes":
            canCommits[n] = True
        elif resp == "Timeout" or resp == "Error":
            canCommits[n] = False
        else:
            print("node %d: received: %r" % (n, resp))
            # abort?

    if not all(canCommits):
        print("canCommit: cannot proceed")
        abort()

    # PHASE 2

    for n in xnodes:
        resp = send(n, "preCommit")
        if resp == "ACK":
            preCommits[n] = True
        elif resp == "Timeout" or resp == "Error":
            preCommits[n] = False
        else:
            print("node %d: received: %r" % (n, resp))

    if not all(preCommits):
        print("preCommit: cannot proceed")
        abort()


    # PHASE 3

    for n in xnodes:
        resp = send(n, "doCommit")
        if resp == "haveCommitted":
            doCommits[n] = True
        elif reps == "Timeout" or resp == "Error":
            doCommits[n] = False
        else:
            print("node %d: received: %r" % (n, resp))

    if not all(doCommits):
        print("commit failed somehow")

    print("success")

def abort():
    print("aborting...")
    # TODO
    sys.exit(1)

def select_best_node(neighbors):
    # select the node with the minimum average ping time
    # the exact mechanism doesn't really matter
    combined = {}
    for n in neighbors.keys():
        for m, ping_time in neighbors[n]:
            combined.setdefault(m, 0)
            combined[m] += ping_time

    best, _ = min(combined.items(), key=operator.itemgetter(1))
    return best

def serverthread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((TCP_IP, TCP_PORT))
    sock.listen(5)

    while 1:
        conn, addr = sock.accept()
        threading.Thread(target=threadConn, args=(conn,)).start()

def main():
    global N

    if len(sys.argv) >= 2:
        N = int(sys.argv[1])


    thr = threading.Thread(target=serverthread, args=())
    thr.daemon = True
    thr.start()
    event.wait()

    print("running")
    run_the_protocol()
    sys.exit(0)

main()
