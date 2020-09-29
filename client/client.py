import socket  
import json
from threading import Thread
import sys
import time

clientSocket = None
clientName = ''

def init():
    global clientSocket
    global clientName
    #address = (sys.argv[0],sys.argv[1])
    address = ('127.0.0.1', 8890)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(address)
    print(clientSocket.recv(1024).decode(encoding='utf8'))
    clientName = input_clientName()
    sendData(clientName, 'CONNECT', '')
    

def input_clientName():
    return input("input client name >> ")

def sendData(clientName, cmd, msg):
    global clientSocket
    jd = {}
    jd['cmd'] = cmd
    jd['name'] = clientName
    jd['data'] = msg
    jsonstr = json.dumps(jd)
    print('send: ' + jsonstr)
    clientSocket.sendall(jsonstr.encode('utf8'))

def recvMsg():
    global clientSocket
    while True:
        try:
            msg = clientSocket.recv(1024).decode(encoding='utf8')
            jd = json.loads(msg)
            cmd = jd['cmd']
            name = jd['name']
            if 'SEND_DATA' == cmd:
                print('recv "%s" msg: "%s"'%(name, jd['data']))
        except Exception as e:
            break

def sendMsg():
    global clientName
    while True:
        msg = input()
        sendData(clientName, 'SEND_DATA', msg)

if __name__ == '__main__':
    init()
    Thread(target = recvMsg).start()
    Thread(target = sendMsg).start()
    while True:
        time.sleep(0.1)
