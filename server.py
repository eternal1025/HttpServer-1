#!/usr/bin/python3

import socketserver
import socket
import sys
import argparse
import os.path
import time
from utils import response

parser = argparse.ArgumentParser(description='Start the HTTP server with custom port and base directory.')

parser.add_argument('-d', '--dir', dest='dir', default=os.path.dirname(__file__),
	help='The base directory where the requested resources will be looked for. Defaults to current directory.')
parser.add_argument('-p', '--port', dest='port', default=80, type = int,
	help='The port where the server will listen. Defaults to HTTP port 80')

args = parser.parse_args()

if not os.path.exists(args.dir):
	sys.exit()

class MyTCPServer(socketserver.TCPServer):
	def server_bind(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(self.server_address)

class MyRequestHandler(socketserver.BaseRequestHandler, response.ResponseHandler):

	def __init__(self, request, client_address, server):
		socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
		

	def handle(self):

		self.request.settimeout(1) # Because recv() is blocking
		data = b''
		while True:
			try:
				msg = self.request.recv(1024)
			except socket.timeout as e:
				err = e.args[0]
				print(err)
				break
			except socket.error as e:
				# Something else happened
				print (e)
				sys.exit(1)
			else:
				if len(msg) == 0:
					print ('No request received')
					sys.exit(0)
				else:
					data = data + msg
		print(data.decode('utf-8'))
		response.ResponseHandler(self.request, data, args.dir)


if __name__ == "__main__":
	
	HOST, PORT = '127.0.0.1', args.port

	try:
		server = MyTCPServer((HOST, PORT), MyRequestHandler)
	except PermissionError :
		print("\nPlease run the server as superuser.\n")
		sys.exit()
	except OSError :
		print("\nSome other service is listening on the specified port.\nPlease use -p [PORT] to specify another one.\n")
		sys.exit()

	try:
		print("Server starting . . .")
		server.serve_forever()
	except KeyboardInterrupt :
		print("\nServer shut down.")
