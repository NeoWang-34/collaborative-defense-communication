import socket
import time
from threading import Thread
from threading import Lock
import sys
import json

class Client:

	__clientSocket = None       # socket to connect the server
	__socket4Detector = None    # socket binded in this device for detectors to connect
	__detectorPool = {}         # detector socket pool
	__recvHistoryList = []      # history list to record received messages from detectors
	__sendHistoryList = {}      # history list to record sent messages to the server, the key is Uri
	__respHistoryList = {}      # history list to record response messages from the server, the key is uri
	__printLock = Lock()

	def __init__(self, clientIp, clientPort, serverIp, serverPort):
		# connect to the server
		self.__clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__clientSocket.connect((serverIp, serverPort))
		# whether the client has connect to the server
		print(self.__clientSocket.recv(1024).decode(encoding='utf8') + '\n')

		# bind socket for communicating with detectors
		self.__socket4Detector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__socket4Detector.bind((clientIp, clientPort))
		self.__socket4Detector.listen(20)
		print("client starts， waiting for detector connecting...\n")

	def acceptDetector(self):
		'''
		create a thread to establish new detector connection
		'''
		while True:
			detectorSocket, detectorAddr = self.__socket4Detector.accept()
			print("Detector " + detectorAddr[0] + ':' + str(detectorAddr[1]) + " connected.\n")
			self.__detectorPool[detectorAddr] = detectorSocket
			# create a thread for each detector to receive message
			thread = Thread(target=self.__recvDetectorMsg, args=(detectorSocket, detectorAddr ))
			thread.setDaemon(True)
			thread.start()

	def __recvDetectorMsg(self, detectorSocket, detectorAddr):
		'''
		create a thread to receive messages from each detector 
		'''
		detectorSocket.sendall("connect client successfully!".encode(encoding='utf8'))
		while True:
			try:
				bytes = detectorSocket.recv(1024)
				msg = bytes.decode(encoding='utf8')
				if len(msg) == 0:
					raise Exception('receive empty message.')
				print('recv Detector ' + detectorAddr[0] + ':' + str(detectorAddr[1]) + ' ->\n' + msg + '\n')
				recvjd = json.loads(msg)
				self.__recvHistoryList.append(recvjd)

				# process according to the message
				if( recvjd['command'] == 'Match'):
					msg = self.__filteringRulesInstall(recvjd)
				else:
					continue
				self.__sendToServer(msg)
			except Exception as e:
				# remove offline detector
				print(e)
				self.__removeDetector(detectorAddr)
				break

	def __removeDetector(self, detectorAddr):
		'''
		remove offline detector
		'''
		detectorSocket = self.__detectorPool[detectorAddr]
		if detectorSocket != None:
			detectorSocket.close()
			self.__detectorPool.pop(detectorAddr)
			print("Detector " + detectorAddr[0] + ':' + str(detectorAddr[1]) + " is offline.\n")

	def __filteringRulesInstall(self, recvjd):
		'''
		filtering rules install
		'''
		jd = {}
		head = {}
		head['Type'] = 'POST'
		head['Code'] = '002'
		try:
			self.__printLock.acquire()
			cuid = input('input cuid: ')
		finally:
			self.__printLock.release()
			time.sleep(0.05)
		head['Uri'] = 'CoDef/FilterRule/cuid=%s/acl=Drop-Tcp-Null' % (cuid)
		data = {}
		ipv4Match = {}
		ipv4Match['srcNetwork'] = recvjd['sourIp'] + '/32'
		ipv4Match['destNetwork'] = recvjd['destIp'] + '/32'
		tcpMatch = {}
		s = recvjd['condition2'][0].split()
		tcpMatch['op'] = s[0]
		tcpMatch['bitmask'] = int(s[1])
		data['Ipv4Match'] = ipv4Match
		data['TcpMatch'] = tcpMatch
		data['Action'] = 'DROP/RATE_LIMIT 20.00'
		jd['Head'] = head
		jd['Data'] = data
		return jd
	
	def __sendToServer(self, msg):
		'''
		send json msg
		'''
		self.__sendHistoryList[msg['Head']['Uri']] = msg
		jdstr = json.dumps(msg, indent=2, separators=(',', ': '))
		print('send to server ' + self.__clientSocket.getpeername()[0] \
			+ ':' + str(self.__clientSocket.getpeername()[1]) + ' ->\n' + jdstr + '\n')
		self.__clientSocket.sendall(jdstr.encode('utf8'))

	def recvFromServer(self):
		'''
		receive response messages from server
		'''
		while True:
			try:
				msg = self.__clientSocket.recv(1024).decode(encoding='utf8')
				jd = json.loads(msg)
				self.__respHistoryList[jd['Head']['Uri']] = jd
				jdstr = json.dumps(jd, indent=2, separators=(',', ': '))
				print('recv respnose msg ->\n' + jdstr + '\n')
			except Exception as e:
				print(e)
				break



if __name__ == '__main__':
	client = Client(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
	Thread(target=client.acceptDetector).start()
	Thread(target=client.recvFromServer).start()