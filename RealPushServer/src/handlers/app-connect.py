#coding:utf-8


"""
app-connect.py
模拟app连接服务器获得设备状态通知
"""

from mantis.fundamental.network.socketutils import SocketConnection,ConnectionEventHandler
from mantis.fundamental.network.message import JsonMessage
from mantis.fundamental.network.accumulator import JsonDataAccumulator
import message


authcode='A001'
ids =['FBXDDD0001']
ids =['FBXDDD0007']
ids =['FBXDDD0004']

class MyConnection(ConnectionEventHandler):
    def __init__(self):
        ConnectionEventHandler.__init__(self)
        self.acc = None

    def onConnected(self,conn,address):
        self.acc = JsonDataAccumulator()
        m = message.MessageAppSubscribe()
        m.authcode = authcode
        m.ids = ids
        conn.sendData(m.marshall())
        print '>> data sent: ', m.marshall()


    def onData(self,conn,data):
        print '<< data in :' , data
        messages = self.acc.enqueue(data)
        for m in messages:
            pass

handle = MyConnection()
conn = SocketConnection(consumer=handle)
# conn.connect('127.0.0.1',17002)

conn.connect('47.100.10.2',9100)
print 'Server Connected ..'
conn.recv()