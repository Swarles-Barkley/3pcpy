#!/usr/bin/env python

import socket
import hashlib
import time
import random
import threading

TCP_IP = '127.0.0.1'
TCP_PORT = 1878
BUFFER_SIZE = 1024
oldtime = int(time.time())
data_lock = threading.Lock()

canCommits = [False,False,False]
preCommits = [False,False,False]
doCommits = [False,False,False]


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(5)

def threadConn(conn):
    data = conn.recv(BUFFER_SIZE)
    if not data: return
    if '\31' not in data: return
    cmd, nodenum = data.split('\31', 1)
    nodenum = int(nodenum)
    #data = data[5:]
    print "data is " + data


    if cmd == "canCommit?":
        with data_lock:
            canCommits[nodenum] = True
            if not all(canCommits):
                conn.send("Wait")
            else:
                conn.send("Yes")

    elif cmd=="preCommit":
        with data_lock:
            preCommits[nodenum] = True
            if not all(preCommits):
                conn.send("Wait")
            else:
                conn.send("ACK")

    elif cmd=="doCommit":
        with data_lock:
            doCommits[nodenum] = True
            if not all(doCommits):
                conn.send("Wait")
            else:
                conn.send("haveCommitted")

    else:
        print("Server doesnt understand: " + data)

    print "server received: ", data

def main():
    while 1:
        conn, addr = sock.accept()
        thr = threading.Thread(target=threadConn, args=(conn,))
        thr.start()
        #conn.send(data)

    conn.close()

main()
