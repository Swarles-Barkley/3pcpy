#!/usr/bin/env python

# pcoord is a coordinator node in the network
# it can be an election coordinator or a regular node in the three phase commit protocol

from __future__ import print_function
import argparse
import json
import operator
import random
import socket
import sys
import threading
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 3878
BASE_PORT = 32400
BUFFER_SIZE = 1024
N = 3 # number of nodes
TIMEOUT = 0.250

data_lock = threading.Lock() # protects the following variables
state = "" # current three-phase-commit node state
nodes = {} # node => nodedata dict
neighbors = {} # node => neighbors list
current_coordinator = None

role = 'node' # or coord; never changes
mynodenum = None
myneighbors = [(i, random.random()) for i in range(N)]

initialized = threading.Event()
done = threading.Event()

stats_lock = threading.Lock()
sent_bytes = 0
received_bytes = 0

# XXX temporarily(?) disabled
send_hello = False

def log(*args):
    if role == 'coord':
        print("[server %s]" % mynodenum, *args)
    else:
        print("[client %s]" % mynodenum, *args)

def threadConn(conn):
    global state
    global winner
    global received_bytes
    def reply(msg):
        global sent_bytes
        r = conn.send(msg)
        with stats_lock:
            sent_bytes += len(msg)
        return r

    try:
        data = conn.recv(BUFFER_SIZE)
        if not data: return
        print("data is", data)
        args = data.split('\37', 2)
        cmd = args[0]
        if len(args) > 1:
            nodenum = int(args[1])
            extra = args[2:]

        ## Coordinator messages
        if cmd == "hello":
            if not send_hello:
                print("warning: got hello")
                return

            #nodedata = json.loads(extra[0])
            #with data_lock:
            #    nodes[nodenum] = nodedata
            #    neighbors[nodenum] = nodedata['nbr']
            #conn.send("ok")

            #if len(nodes) >= N:
            #    initialized.set()

        elif cmd == "startVote":
            with data_lock:
                candidate = nodenum
            conn.send("OK")
            start_election() # ?
            # TODO
            # wait 15-30 seconds in case other nodes also sent startVote
            # abort currently-running election, if any?
            # inform other nodes about the vote...

        ## node messages
        else:
            if cmd == "canCommit?":
                with data_lock:
                    state = "waiting"
                    #candidate = extra[0]
                # XXX send table
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
                    #winner = candidate
                reply("haveCommitted")
                done.set()

            else:
                print("Server doesnt understand: " + data)
    finally:
        conn.close()


def get_port_for_node(nodenum):
    return BASE_PORT + nodenum

    #XXX
    with data_lock:
        port = nodes[nodenum]["port"]
    return port

def send(nodenum, msg):
    global sent_bytes
    global received_bytes
    port = get_port_for_node(nodenum)
    addr = (TCP_IP, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        sock.connect(addr)
        sock.send(msg)
        with stats_lock:
            sent_bytes += len(msg)
        data = sock.recv(BUFFER_SIZE)
        with stats_lock:
            received_bytes += len(data)
        return data
    except socket.timeout:
        return "Timeout"
    except socket.error:
        return "Error"
    finally:
        sock.close()


def send_data(nodenum, msg, extra):
    data = msg + "\37" + json.dumps(extra)

def run_an_election():
    # wait a random amount of time...
    #
    #

    canCommits = [False]*N
    preCommits = [False]*N
    doCommits = [False]*N

    # this node doesn't count as part of the election
    canCommits[mynodenum] = True
    preCommits[mynodenum] = True
    doCommits[mynodenum] = True

    # TODO: move after phase 1
    with data_lock:
        winner = select_best_node(neighbors)
    print("electing node %s" % winner)

    # XXX
    #with data_lock:
    #    xnodes = nodes.copy()

    xnodes = list(xrange(0,N))
    xnodes.remove(mynodenum)

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
        abort(xnodes)

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
        abort(xnodes)


    # PHASE 3

    for n in xnodes:
        resp = send(n, "doCommit")
        if resp == "haveCommitted":
            doCommits[n] = True
        elif resp == "Timeout" or resp == "Error":
            doCommits[n] = False
        else:
            print("node %d: received: %r" % (n, resp))

    if not all(doCommits):
        print("commit failed somehow")

    print("success")

def abort(xnodes):
    print("aborting...")
    # TODO
    aborted = [False]*N
    for n in xnodes:
        resp = send(n, "doAbort")
        if resp == "haveAborted":
            aborted[n] = True
        elif resp == "Timeout" or resp == "Error":
            aborted[n] = False
        else:
            print("node %d: received: %r" % (n, resp))
    sys.exit(1)

def select_best_node(neighbors):
    return 0 # XXX

    # select the node with the minimum average ping time
    # the exact mechanism doesn't really matter
    combined = {}
    for n in neighbors.keys():
        for m, ping_time in neighbors[n]:
            combined.setdefault(m, 0)
            combined[m] += ping_time

    best, _ = min(combined.items(), key=operator.itemgetter(1))
    return best

def serverthread(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((TCP_IP, port))
    sock.listen(5)

    while 1:
        conn, addr = sock.accept()
        thr = threading.Thread(target=threadConn, args=(conn,))
        thr.start()

def node_serverthread(sock):
    while 1:
        conn, addr = sock.accept()
        thr = threading.Thread(target=threadConn, args=(conn,))
        thr.start()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("nodenum", type=int, help="the number of this node")
    parser.add_argument("N", type=int, help="the total number of nodes")
    parser.add_argument("--coord", action="append", type=int,
        help="indicates the number of a coordinator node")
    #parser.add_argument("--coord", action="store_true", help="indicates that this node is a coordinator"))
    #parser.add_argument("--add-coord", action="append", help="port of a coordinator")
    return parser.parse_args()

def main():
    global N
    global MY_PORT
    global mynodenum
    global role

    args = parse_args()
    N = args.N
    MY_PORT = BASE_PORT + args.nodenum
    mynodenum = args.nodenum

    if args.nodenum in args.coord:
        role = 'coord'

        thr = threading.Thread(target=serverthread, args=(MY_PORT,))
        thr.daemon = True
        thr.start()
        if send_hello:
            initialized.wait()

        time.sleep(1)
        print("running")
        run_an_election()
        sys.exit(0)

    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((TCP_IP, MY_PORT))
        sock.listen(5)

        if send_hello:
            data = trysend("hello\37"+str(nodenum)+"\37" + json.dumps(nodedata))
            log("sent hello, received:", data)

        thr = threading.Thread(target=node_serverthread, args=(sock,))
        thr.daemon = True
        thr.start()

        done.wait()

        log("final state:", state)
        with stats_lock:
            log("sent %d bytes" % sent_bytes)
            log("received %d bytes" % received_bytes)

        #sock.close()


main()
