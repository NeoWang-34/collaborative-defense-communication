import socket
from threading import Thread
import sys
import time
import json

serverSocket = None
clientSocketPool = {}  # client socket pools

def init():
    """
    initialize server
    """
    global serverSocket
    #address = (sys.argv[0],sys.argv[1])
    address = ('127.0.0.1', 8889)
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    serverSocket.bind(address)
    serverSocket.listen(10)
    print("server start，wait for client connecting...")

def accept_client():
    """
    establish new client connection
    """
    global serverSocket
    while True:
        clientSocket, clientAddr = serverSocket.accept()
        # create an independent thread for each client to receive messages
        thread = Thread(target=recvMsg, args=(clientSocket, clientAddr))
        thread.setDaemon(True)
        thread.start()


def recvMsg(clientSocket, clientAddr):
    """
    handle received messages
    """
    global clientSocketPool
    clientSocket.sendall("connect server successfully!".encode(encoding='utf8'))
    while True:
        try:
            bytes = clientSocket.recv(1024)
            msg = bytes.decode(encoding='utf8')
            '''
            jd = json.loads(msg)
            cmd = jd['cmd']
            clientName = jd['name']
            if 'CONNECT' == cmd:
                clientSocketPool[clientName] = clientSocket
                print('on client connect: ' + clientName, clientAddr)
            elif 'SEND_DATA' == cmd:
                print('recv "%s" msg: "%s"'%(clientName, jd['data']))
                '''
            print('recv :' + msg)
        except Exception as e:
            print(e)
            removeClient(clientName)
            break

def removeClient(clientName):
    """
    remove offline client
    """
    global clientSocketPool
    clientSocket = clientSocketPool[clientName]
    if None != clientSocket:
        clientSocket.close()
        clientSocketPool.pop(clientName)
        print("client offline: " + clientName)

def sendMsg():
    """
    send messages from server
    """
    while True:
        msg = input()
        if msg != '':
            clientName = input('Input client name >>')
            sendMsgTo(clientName, msg)

def sendMsgTo(clientName, msg):
    """
    send messages to client
    """
    global clientSocketPool
    clientSocket = clientSocketPool[clientName]
    jd = {}
    jd['cmd'] = "SEND_DATA"
    jd['name'] = "server"
    jd['data'] = msg
    jsonstr = json.dumps(jd)
    print('send: ' + jsonstr)
    clientSocket.sendall(jsonstr.encode('utf8'))

if '__main__' == __name__:
    init()
    Thread(target=accept_client).start()
    Thread(target=sendMsg).start()
    # main thread
    while True:
        time.sleep(0.1)
