#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

#https://github.com/liris/websocket-client
## sudo pip install --user websocket-client
from websocket import create_connection
import sys, os
from json import loads
from subprocess import call
from datetime import datetime

import time

class mailbox(object):
	"""10 minute mailbox"""
	def __init__(self):
		super(mailbox, self).__init__()
		self.ws = create_connection("wss://dropmail.me/websocket")
		self.next = self.ws.recv
		self.close = self.ws.close
		self.email = self.next()[1:].split(":")[0]
		self.next()

	def getMailAdd(self):
		#print self.email
		return self.email

	def getCorreo(self):
		while True:
			result = self.next() #Se queda aquí parado

			try:
				#print("Recieved following at {0}".format( datetime.now()))
				for k in loads(result[1:]).items():
					if "text" == k[0]:
						#print k[1]
						return k[1]
					#print("\t%s: %s" % k)
			except:
				pass

def main(box):
	box.getMailAdd()
	time.sleep(10)
	box.getCorreo()



if __name__ == '__main__':
	#print("PID: {0}\nIf you can't quite, run 'kill {0}'\n".format(os.getpid()))
	try:
		box = mailbox()
		main(box)
	except KeyboardInterrupt:
		box.close()
		sys.exit(0)
