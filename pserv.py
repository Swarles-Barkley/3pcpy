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
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        if '\31' not in data: break
        cmd, nodenum = data.split('\31', 1)
        nodenum = int(nodenum)
        #data = data[5:]
        print "data is " + data
        if (cmd == "canCommit?"):
            data_lock.acquire()
            canCommits[nodenum] = True
            if(False in canCommits):
                data_lock.release()
                conn.send("Wait")
                break
            else:
                data_lock.release()
                conn.send("Yes")
                break
        elif(cmd=="preCommit"):
            data_lock.acquire()
            preCommits[nodenum] = True
            if(False in preCommits):
                data_lock.release()
                conn.send("Wait")
                break
            else:
                data_lock.release()
                conn.send("ACK")
                break
        elif(cmd=="doCommit"):
            data_lock.acquire()
            doCommits[nodenum] = True
            if(False in doCommits):
                data_lock.release()
                conn.send("Wait")
                break
            else:
                data_lock.release()
                conn.send("haveCommitted")
                break
        else:
            print("Server doesnt understand: " + data)
            break
        print "server received: ", data

def main():
    while 1:
        conn, addr = sock.accept()
        thr = threading.Thread(target=threadConn, args=(conn,))
        thr.start()
        #conn.send(data)

    conn.close()

main()
