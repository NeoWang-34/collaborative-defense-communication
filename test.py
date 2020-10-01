import json
import time
from threading import Thread
from threading import Lock

lock = Lock()

def work(s):
    while True:
        lock.acquire()
        a=input(s)
        if(a==''):
            print('f')
        else:
            print(a)
        lock.release()
        time.sleep(0.05)

Thread(target=work,args=('1:',)).start()
Thread(target=work,args=('2:',)).start()
'''import signal

class InputTimeoutError(Exception):
    pass

def interrupted(signum, frame):
    raise InputTimeoutError


signal.signal(signal.SIGALRM, interrupted)
signal.alarm(2)

while True:
    try:
        name = input('请在2秒内输入你的名字：')
    except InputTimeoutError:
        print('\ntimeout')
        signal.alarm(2)
        continue
    else:
        break

signal.alarm(0)  # 读到输入的话重置信号
print('你的名字是：%s' % name)'''
