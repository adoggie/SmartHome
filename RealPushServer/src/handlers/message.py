#coding:utf-8

"""
app 连接登录消息
"""
from mantis.fundamental.network.message import JsonMessage
from mantis.fanbei.smarthome.base import *

APP_MESSAGE_JOIN = "join"
APP_MESSAGE_ACCEPT = "accept"
APP_MESSAGE_REJECT = "reject"
APP_MESSAGE_HEARTBEAT = "heartbeat"
APP_MESSAGE_SUBSCRIBE = "subscribe"
APP_MESSAGE_UNSUBSCRIBE = "unsubscribe"


Message = JsonMessage


# class MessageAppJoin(Message):
#     """app 上线"""
#     NAME = APP_MESSAGE_JOIN
#
#     def __init__(self):
#         Message.__init__(self, self.NAME)
#         self.authcode = ''  # 授权码

class MessageAppHeartbeat(Message):
    """app 心跳"""
    NAME = APP_MESSAGE_HEARTBEAT

    def __init__(self):
        Message.__init__(self, self.NAME)

class MessageAppSubscribe(Message):
    """app 订阅设备消息"""
    NAME = APP_MESSAGE_SUBSCRIBE

    def __init__(self):
        Message.__init__(self, self.NAME)
        self.authcode = ''  # 授权码
        self.ids = []

class MessageAppUnSubscribe(Message):
    """app 订阅设备消息"""
    NAME = APP_MESSAGE_UNSUBSCRIBE

    def __init__(self):
        Message.__init__(self, self.NAME)
        self.authcode = ''  # 授权码
        self.ids = []       # 设备编号


# class MessageAppAccept(Message):
#     """app accept"""
#     NAME = APP_MESSAGE_ACCEPT
#
#     def __init__(self):
#         Message.__init__(self, self.NAME)
#
# class MessageAppReject(Message):
#     """app reject"""
#     NAME = APP_MESSAGE_REJECT
#
#     def __init__(self):
#         Message.__init__(self, self.NAME)

MessageClsDict ={}

def registerMessageObject(msgcls):
    MessageClsDict[msgcls.NAME] = msgcls


for key,value in locals().items():
    if key.find('Message')==0 and key not in ('Message','MessageClsDict'):
        registerMessageObject(value)

def parseMessage(data):
    print data
    if  isinstance(data,str):
        data = json.loads(data)

    message = data.get('name')
    msgcls = MessageClsDict.get(message)
    if not msgcls:
        print 'Message Type unKnown. value:{}'.format(message)
        return None
    data = data.get('values',{})
    msg = msgcls()
    msg.assign(data)
    return msg

