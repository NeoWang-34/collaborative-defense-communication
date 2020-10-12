import socket
from threading import Thread
import sys
import json

class Detector:

	__detectorSocket = None  # socket to connect to the client
	__historyList = []       # history list to record messages that has been sent

	def __init__(self, clientIp, clientPort):
		# connect to the client
		self.__detectorSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__detectorSocket.connect((clientIp, clientPort))
		# whether the detector has connect to the client
		print(self.__detectorSocket.recv(1024).decode(encoding='utf8'))

	def sendMsg(self):
		'''
		design cmd here
		'''
		while True:
			cmd = input('>>')
			if cmd == 'History':
				# show history list
				jdstr = json.dumps(self.__historyList, indent=2, separators=(',', ': '))
				print(jdstr)
			elif cmd == 'Match':
				# handle cmd -Match-
				sourIp = input('sourIp:')
				destIp = input('destIp:')
				print('condition1->')
				condition1 = {}
				length = input('length:')
				if length != '':
					condition1['length'] = int(length)
				protocol = input('protocol')
				if protocol != '':
					condition1['protocol'] = protocol
				if fragment != '':
					condition1['fragment'] = fragment	
				sourPort = input('sourPort:')
				destPort = input('destPort:')
				print('condition2->')
				condition2 = {}
				protocol = input('protocol')
				if protocol == 'TCP':
					bitmask = input('bitmask:')
					if bitmask != '':
						condition2['bitmask'] = bitmask
				elif protocol == 'UDP':
					length = input('length:')
					if length != '':
						condition2['length'] = int(length)
				elif protocol == 'ICMP':
					Type = input('type:')
					if Type != '':
						condition2['type'] = int(Type)
					code = ipnut('code:')
					if code != '':
						condition2['code'] = int(code)

				msg = self.__dataToMsg(cmd, sourIp, destIp, condition1, sourPort, destPort, condition2)
				self.__sendToClient(msg)
			else:
				print('  Sorry, no such cmd!\n' +
					  '  usable cmd:\n' +
					  '      History    -- to show the sent history\n' +
					  '      Match      -- to send Match cmd\n')

	def __dataToMsg(self, command, sourIp, destIp, condition1, sourPort, destPort, condition2):
		'''
		generate and save cmd
		'''
		msg = {}
		msg['command'] = command
		msg['sourIp'] = sourIp
		msg['destIp'] = destIp
		msg['condition1'] = condition1
		msg['sourPort'] = sourPort
		msg['destPort'] = destPort
		msg['condition2'] = condition2
		# save to historyList
		self.__historyList.append(msg)
		return msg

	def __sendToClient(self, msg):
		'''
		send json msg
		'''
		jdstr = json.dumps(msg, indent=2, separators=(',', ': '))
		print('send to client ' + self.__detectorSocket.getpeername()[0] \
			+ ':' + str(self.__detectorSocket.getpeername()[1]) + ' ->\n' + jdstr)
		self.__detectorSocket.sendall(jdstr.encode('utf8'))

if __name__ == '__main__':
	# connect to the client
	detector = Detector(sys.argv[1],int(sys.argv[2]))
	# send msg to the client
	Thread(target = detector.sendMsg).start()