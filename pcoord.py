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
BASE_PORT = 12000
BUFFER_SIZE = 1024
N = 3 # number of nodes
TIMEOUT = 0.250
RETRIES = 3 # number of times to retry a phase
QUORUM = 1.0
FAILURE = 0.0 # transient failure rate

data_lock = threading.Lock() # protects the following variables
state = "" # current three-phase-commit node state
nodes = {} # node => nodedata dict
winner = None # current elected coordinator
candidate = None

role = 'node' # or coord; never changes
mynodenum = None
myneighbors = []
topology = []

initialized = threading.Event()
done = threading.Event()

stats_lock = threading.Lock()
sent_bytes = 0
received_bytes = 0

# if send_hello is enabled, each node will ping the initial coordinator at startup,
# and the initial coordinator will wait to hear from all nodes before starting an election.
# this just lets us get all our sockets open before trying anything
send_hello = True

def log(*args):
    if role == 'coord':
        print("[server %s]" % mynodenum, *args)
    else:
        print("[client %s]" % mynodenum, *args)

def random_failure():
    return random.random() <= FAILURE

def threadConn(conn):
    global state
    global winner
    global candidate
    global received_bytes
    def reply(msg):
        global sent_bytes
        with stats_lock:
            sent_bytes += len(msg)
        if random_failure():
            # simulate transient packet loss
            log("dropping response:", msg)
            conn.send("Timeout")
            return 0
        r = conn.send(msg)
        return r

    try:
        data = conn.recv(BUFFER_SIZE)
        if not data: return
        log("data is", data)
        args = data.split('\37', 2)
        cmd = args[0]
        if len(args) > 1:
            nodenum = int(args[1])
            extra = args[2:]

        if cmd != "hello":
            with stats_lock:
                received_bytes += len(data)

        ## Coordinator messages
        if cmd == "hello":
            if not send_hello:
                log("warning: got hello")
            else:
                with data_lock:
                    nodes[nodenum] = 1
                    ready = (len(nodes) >= N)

                # not reply() because can't fail and don't want to contribute to stats
                conn.send("ok")
                if ready:
                    initialized.set()

        elif cmd == "startVote" and role == "coord":
            with data_lock:
                candidate = nodenum
            reply("OK")
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
                # Send neighbor table along with response
                reply("Yes\37"+str(mynodenum)+"\37"+json.dumps(myneighbors))

            elif cmd == "preCommit":
                with data_lock:
                    state = "precommit"
                    candidate = int(extra[0])
                reply("ACK")

            elif cmd == "doAbort":
                with data_lock:
                    state = "aborted"
                reply("haveAborted")
                #done.set()

            elif cmd == "doCommit":
                with data_lock:
                    state = "committed"
                    winner = candidate
                reply("haveCommitted")
                #done.set()

            elif cmd == "kill":
                log("killed")
                done.set()
                #sys.exit(1)

            else:
                log("Server doesnt understand: " + data)
    finally:
        conn.close()


def get_port_for_node(nodenum):
    return BASE_PORT + nodenum

    #XXX
    with data_lock:
        port = nodes[nodenum]["port"]
    return port

def send(nodenum, msg, can_fail=True, stats=True):
    global sent_bytes
    global received_bytes
    if stats:
        with stats_lock:
            sent_bytes += len(msg)
    if can_fail and topology and not topology[nodenum][mynodenum]:
        log("node %d out of range:" % nodenum, msg)
        return "Timeout"
    if can_fail and random_failure():
        # simulate transient packet loss
        log("dropping packet to %d:" % nodenum, msg)
        return "Timeout"
    port = get_port_for_node(nodenum)
    addr = (TCP_IP, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    try:
        sock.connect(addr)
        sock.send(msg)
        data = sock.recv(BUFFER_SIZE)
        if stats:
            with stats_lock:
                received_bytes += len(data)
        return data
    except socket.timeout:
        return "Timeout"
    except socket.error:
        return "Error"
    finally:
        sock.close()

class Timeout(Exception):
    """Request timed out"""

def trysend(nodenum, msg):
    """trysend sends a message to a node, but retries if it encounters an error.
    does not contribute to stats, and is not affected by imaginary transient failures"""
    for sanity in range(30):
        data = send(nodenum, msg, can_fail=False, stats=False)
        if data and data != "Wait" and data != "Timeout" and data != "Error":
            return data
        time.sleep(1)

    raise Timeout()

def send_data(nodenum, cmd, extra):
    """send_data sends a command with associated data,
    which should be a json-serializable object"""
    msg = cmd + "\37" + str(mynodenum) + "\37" + json.dumps(extra)
    return send(nodenum, msg)

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

    # XXX
    #with data_lock:
    #    xnodes = nodes.copy()

    xnodes = list(xrange(0,N))
    xnodes.remove(mynodenum)

    neighbors = {} # node => neighbors list

    # PHASE 1
    for retry in xrange(RETRIES):
        # TODO: send requests in parallel
        # TODO: count each phase as only sending one message?
        for n in xnodes:
            if canCommits[n]:
                continue

            data = send(n, "canCommit?")

            args = data.split('\37', 2)
            resp = args[0]

            if resp == "Yes":
                nodenum = int(args[1])
                nbrs = json.loads(args[2])
                with data_lock:
                    neighbors[nodenum] = nbrs
                canCommits[n] = True
            elif resp == "Timeout" or resp == "Error":
                canCommits[n] = False
            else:
                log("node %d: received: %r" % (n, resp))
                # abort?

        if quorumOf(canCommits):
            break

        log("canCommit failed (retry %d)" % retry)
        print(canCommits)

    if not quorumOf(canCommits):
        log("canCommit: cannot proceed")
        abort(xnodes)
        return

    candidate = select_best_node(neighbors)
    log("electing node %s" % candidate)

    # PHASE 2

    for retry in xrange(RETRIES):
        for n in xnodes:
            if preCommits[n]:
                continue

            resp = send_data(n, "preCommit", candidate)
            if resp == "ACK":
                preCommits[n] = True
            elif resp == "Timeout" or resp == "Error":
                preCommits[n] = False
            else:
                log("node %d: received: %r" % (n, resp))

        if quorumOf(preCommits):
            break

        log("preCommit failed (retry %d)" % retry)

    if not quorumOf(preCommits):
        log("preCommit: cannot proceed")
        abort(xnodes)
        return


    # PHASE 3

    for retry in xrange(RETRIES):
        for n in xnodes:
            if doCommits[n]:
                continue
            resp = send(n, "doCommit")
            if resp == "haveCommitted":
                doCommits[n] = True
            elif resp == "Timeout" or resp == "Error":
                doCommits[n] = False
            else:
                log("node %d: received: %r" % (n, resp))

        if quorumOf(doCommits):
            break

        log("commit failed (retry %d)" % retry)

    acks = sum(1 for x in doCommits if x)
    log("%d of %d nodes acknowledged the commit" % (acks, N))

    if not quorumOf(doCommits):
        log("commit failed somehow")
    else:
        log("success")

def abort(xnodes):
    log("aborting...")
    # TODO
    aborted = [False]*N
    for n in xnodes:
        resp = send(n, "doAbort")
        if resp == "haveAborted":
            aborted[n] = True
        elif resp == "Timeout" or resp == "Error":
            aborted[n] = False
        else:
            log("node %d: received: %r" % (n, resp))

def cleanup(xnodes):
    """cleans up at the end of an election by sending all other nodes a "Kill" message"""
    log("cleaning up")
    for n in xnodes:
        send(n, "kill", can_fail=False, stats=False)


def quorumOf(values):
    q = sum(1 for x in values if x)
    return q >= int(len(values) * QUORUM)

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

def serverthread(sock):
    sock.settimeout(TIMEOUT)
    while not done.is_set():
        try:
            conn, addr = sock.accept()
        except socket.timeout:
            continue
        else:
            thr = threading.Thread(target=threadConn, args=(conn,))
            thr.start()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("nodenum", type=int, help="the number of this node")
    parser.add_argument("N", type=int, help="the total number of nodes")
    parser.add_argument("--coord", action="append", type=int, dest="coords",
        help="indicates the number of a coordinator node; specify once for each coordinator")
    parser.add_argument("--quorum", action="store", type=float, default=None,
        help="the required quorum level between 0.0 and 1.0")
    parser.add_argument("--failure", action="store", type=float, default=None,
        help="the transient failure rate (drop rate) between 0.0 and 1.0")
    # TODO: topology type
    parser.add_argument("--topology", action="store_true",
        help="generate a randomly-connected network topology")
    parser.add_argument("--topology-seed", type=int, default=1,
        help="seed for generating the topology matrix; must be the same for all nodes")
    parser.add_argument("--seed", type=int, default=None,
        help="seed for other randomness")
    return parser.parse_args()

def generate_topology(seed, p):
    """generates a topology matrix for the network in which nodes are connected with probability p"""
    top = [[1]*N for _ in xrange(N)]
    rng = random.Random(seed)
    for i in xrange(0, N):
        for j in xrange(i, N):
            connected = (rng.random() < p)
            top[i][j] = connected
            top[j][i] = connected

    return top

def main():
    global N
    global MY_PORT
    global QUORUM
    global FAILURE
    global mynodenum
    global myneighbors
    global role
    global topology

    args = parse_args()
    if args.seed:
        random.seed(args.seed + args.nodenum)
    else:
        random.seed(1234 + args.nodenum)
    N = args.N
    MY_PORT = BASE_PORT + args.nodenum
    mynodenum = args.nodenum
    # TODO: generate neighbors based on topology
    myneighbors = [(i, random.random()) for i in args.coords]
    if args.quorum is not None:
        QUORUM = args.quorum
    if args.failure is not None:
        FAILURE = args.failure
    if args.topology:
        topology = generate_topology(args.topology_seed, .90)


    if args.nodenum in args.coords:
        role = 'coord'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind((TCP_IP, MY_PORT))
    sock.listen(100)

    initial_coordinator = args.coords[0]

    if mynodenum == initial_coordinator:
        nodes[mynodenum] = 1

        thr = threading.Thread(target=serverthread, args=(sock,))
        thr.daemon = True
        thr.start()

        if send_hello:
            initialized.wait()
        else:
            time.sleep(1)


        log("running an election")
        a = time.time()
        run_an_election()
        d = time.time() - a
        log("took %f seconds" % d)

        time.sleep(.5)
        cleanup([i for i in xrange(N) if i != mynodenum])

    else:
        if send_hello:
            nodedata = {"port": MY_PORT}
            data = trysend(initial_coordinator, "hello\37"+str(mynodenum)+"\37" + json.dumps(nodedata))
            log("sent hello, received:", data)

        #if mynodenum == 8:
        #    log("node 8 crashing")
        #    sys.exit(1)

        thr = threading.Thread(target=serverthread, args=(sock,))
        #thr.daemon = True
        thr.start()

        done.wait()

        #sock.close()

    log("final state:", state)
    log("winner:", winner)
    with stats_lock:
        log("sent %d bytes" % sent_bytes)
        log("received %d bytes" % received_bytes)


main()
