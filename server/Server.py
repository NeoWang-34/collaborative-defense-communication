import socket
from threading import Thread
from threading import Lock
import sys
import json

class Server:

	__serverSocket = None     # socket binded in server for clients to connect
	__clientPool = {}         # client socket pool
	__recvHistoryList = {}    # history list to record received messages from the client, the key is Uri
	__sendHistoryList = {}    # history list to record response messages to the client, the key is uri

	def __init__(self, serverIp, serverPort):
		# bind socket for communicating with clients
		self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
		self.__serverSocket.bind((serverIp, serverPort))
		self.__serverSocket.listen(20)
		print("server start，wait for client connecting...\n")
	
	def acceptClient(self):
		'''
		establish new client connection
		'''
		while True:
			clientSocket, clientAddr = self.__serverSocket .accept()
			print("Client " + clientAddr[0] + ':' + str(clientAddr[1]) + " connected.\n")
			self.__clientPool[clientAddr] = clientSocket
			# create an independent thread for each client to receive messages
			thread = Thread(target=self.__recvClientMsg, args=(clientSocket, clientAddr))
			thread.setDaemon(True)
			thread.start()

	def __recvClientMsg(self, clientSocket, clientAddr):
		'''
		create a thread to receive messages from each client 
		'''
		clientSocket.sendall("connect server successfully!".encode(encoding='utf8'))
		while True:
			try:
				bytes = clientSocket.recv(1024)
				msg = bytes.decode(encoding='utf8')
				if len(msg) == 0:
					raise Exception('receive empty message.')
				print('recv Client ' + clientAddr[0] + ':' + str(clientAddr[1]) + ' ->\n' + msg + '\n')
				recvjd = json.loads(msg)
				self.__recvHistoryList[recvjd["Head"]["Uri"]] = recvjd

				# process according to the message
				if( recvjd['Head']['Uri'].endswith('Drop-Tcp-Null') ):
					msg = self.__filteringRulesInstall(recvjd)
				else:
					continue
				self.__sendToClient(msg, clientSocket)
			except Exception as e:
				# remove offline client
				print(e + '\n')
				self.__removeClient(clientAddr)
				break

	def __removeClient(self, clientAddr):
		'''
		remove offline client
		'''
		clientSocket = self.__clientPool[clientAddr]
		if clientSocket != None:
			clientSocket.close()
			self.__clientPool.pop(clientAddr)
			print("client " + clientAddr[0] + ':' + str(clientAddr[1]) + " is offline.\n")

	def __filteringRulesInstall(self, recvjd):
		jd = {}
		head = {}
		head['Type'] = 'CREATED'
		head['Code'] = '201'
		head['Uri']  = recvjd['Head']['Uri']
		jd['Head'] = head
		return jd

	def __sendToClient(self, msg, clientSocket):
		'''
		send response msg to client
		'''
		self.__sendHistoryList[msg['Head']['Uri']] = msg
		jdstr = json.dumps(msg, indent=2, separators=(',', ': '))
		print('send to client ' + clientSocket.getpeername()[0] \
			+ ':' + str(clientSocket.getpeername()[1]) + ' ->\n' + jdstr +'\n')
		clientSocket.sendall(jdstr.encode('utf8'))

if __name__ == '__main__':
	server = Server(sys.argv[1], int(sys.argv[2]))
	Thread(target=server.acceptClient).start()
