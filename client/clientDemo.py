import socket
import threading
 
 
inString = ''
outString = ''
nick = ''
 
def DealOut(s):
    global nick, outString
    while True:
        outString = input("input:")
        outString = nick + ': ' + outString
        s.send(outString.encode('utf8'))
 
def DealIn(s):
    global inString
    while True:
        try:
            inString = s.recv(1024).decode(encoding='utf8')
            print("recv:" + inString)
        except:
            break
        
 
nick = input("input your nickname: ")
ip = "127.0.0.1"
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, 8888))
sock.send(nick.encode('utf8'))
 
threading.Thread(target = DealIn, args = (sock,)).start()
threading.Thread(target = DealOut, args = (sock,)).start()
 
#sock.close()