import socket
from threading import Thread
import sys
import json

class Client:

    __clientSocket = None       # socket to connect the server
    __socket4Detector = None    # socket binded in this device for detectors to connect
    __detectorPool = {}         # detector socket pool
    __recvHistoryList = []      # history list to record received messages from detectors
    __sendHistoryList = {}      # history list to record sent messages to the server, the key is Uri
    __respHistoryList = {}      # history list to record response messages from the server, the key is Uri

    def __init__(self, clientIp, clientPort, serverIp, serverPort):
        # connect to the server
        self.__clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__clientSocket.connect((serverIp, serverPort))
        # whether the client has connect to the server
        print(self.__clientSocket.recv(1024).decode(encoding='utf8'))

        # bind socket for communicating with detectors
        self.__socket4Detector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
        self.__socket4Detector.bind((clientIp, clientPort))
        self.__socket4Detector.listen(10)
        print("client start，wait for detector connecting...")

    def acceptDetector(self):
        '''
        create a thread to establish new detector connection
        '''
        while True:
            detectorSocket, detectorAddr = self.__socket4Detector.accept()
            self.__detectorPool[detectorAddr] = detectorSocket
            # create a thread for each detector to receive message
            thread = Thread(target=self.__recvDetectorMsg, args=(detectorSocket, detectorAddr ))
            thread.setDaemon(True)
            thread.start()
    
    def __recvDetectorMsg(self, detectorSocket, detectorAddr):
        '''
        create a thread for each detector to receive message
        '''
        detectorSocket.sendall("connect client successfully!".encode(encoding='utf8'))
        while True:
            try:
                bytes = detectorSocket.recv(1024)
                msg = bytes.decode(encoding='utf8')
                print('recv ->\n' + msg)
                jd = json.loads(msg)
                self.__recvHistoryList.append(jd)
            except Exception as e:
                # remove offline detector
                print(e)
                self.__removeDetector(detectorAddr)
                break

    def __removeDetector(self, detectorAddr):
        """
        remove offline detector
        """
        detectorSocket = self.__detectorPool[detectorAddr]
        if detectorSocket != None:
            detectorSocket.close()
            self.__detectorPool.pop(detectorSocket)
            print("Detector " + detectorAddr[0] + ':' + str(detectorAddr[1]) + " offline.")
