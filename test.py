import json
import time
from threading import Thread

data = [ { 'a' : 1, 'b' : [2,222,22], 'c' : 3, 'd' : 4, 'e' : 5 }, {'f':6, 'g':7} ]

data2 = json.dumps(data, indent=4, separators=(',', ': '))
data3 = json.loads(data2)

def work():
    time.sleep(2)
    print('abasdasd')
    print('123asdqwe')
    print('>>',end='')

Thread(target=work).start()
a = input(">>")
print(a)