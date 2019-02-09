#!/usr/bin/env python

import socket
import hashlib
import time
import random
from thread import *
import threading
	
TCP_IP = '127.0.0.1'
TCP_PORT = 1878
BUFFER_SIZE = 1024
oldtime = int(time.time())
conn_lock = threading.Lock()
data_lock = threading.Lock()

canCommits = [False,False,False]
preCommits = [False,False,False]
doCommits = [False,False,False]


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(5)

def threadConn(c):
	while 1:
		data = conn.recv(BUFFER_SIZE)
		if not data: break
		delim1 = data.find('\31')
		cmd = data[:delim1]
		nodenum = int(data[delim1+1:])
		#data = data[5:]
		print "data is " + data
		if (cmd == "canCommit?"):
			data_lock.acquire()
			canCommits[nodenum] = True
			if(False in canCommits):
				data_lock.release()
				conn.send("Wait")
				conn_lock.release()
				break
			else:
				data_lock.release()
				conn.send("Yes")
				conn_lock.release()
				break
		elif(cmd=="preCommit"):
			data_lock.acquire()
			preCommits[nodenum] = True
			if(False in preCommits):
				data_lock.release()
				conn.send("Wait")
				conn_lock.release()
				break
			else:
				data_lock.release()
				conn.send("ACK")
				conn_lock.release()
				break
		elif(cmd=="doCommit"):
			data_lock.acquire()
			doCommits[nodenum] = True
			if(False in doCommits):
				data_lock.release()
				conn.send("Wait")
				conn_lock.release()
				break
			else:
				data_lock.release()
				conn.send("haveCommitted")
				conn_lock.release()
				break
		else:
			print("Server doesnt understand: " + data)
			conn_lock.release()
			break
		print"server received: ", data

while 1:
	conn, addr = sock.accept()
	conn_lock.acquire()
	start_new_thread(threadConn, (conn,))
	#conn.send(data)
conn.close()
