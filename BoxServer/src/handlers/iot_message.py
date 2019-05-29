#coding:utf-8

"""
华为iot设备协议转换
"""
from mantis.fundamental.network.message import JsonMessage
from mantis.fanbei.smarthome.base import *

IOT_MESSAGE_DEVICE_ONLINE = "device_online"
IOT_MESSAGE_DEVICE_OFFLINE = "device_offline"
IOT_MESSAGE_SENSOR_DEVICE_ONLINE = "sensor_device_offline"
IOT_MESSAGE_SENSOR_DEVICE_OFFLINE = "sensor_device_offline"
IOT_MESSAGE_SENSOR_DEVICE_STATUS_REPORT = "sensor_device_status_report"
IOT_MESSAGE_DEVICE_COMMAND = "device_command"
IOT_MESSAGE_HEARTBEAT = "heartbeat"

class MessageIotMessage(JsonMessage):
    NAME = 'iot_message'

    def __init__(self,name ):
        JsonMessage.__init__(self, name)
        self.device_id = ''

class IotMessageDeviceOnline(MessageIotMessage):
    """设备上线"""
    NAME = IOT_MESSAGE_DEVICE_ONLINE

    def __init__(self):
        MessageIotMessage.__init__(self, self.NAME)

class IotMessageDeviceOffline(MessageIotMessage):
    """设备离线"""
    NAME = IOT_MESSAGE_DEVICE_OFFLINE

    def __init__(self):
        MessageIotMessage.__init__(self, self.NAME)

class IotMessageHeartbeat(MessageIotMessage):
    """"""
    NAME = IOT_MESSAGE_HEARTBEAT

    def __init__(self):
        MessageIotMessage.__init__(self, self.NAME)


class IotMessageSensorDeviceOnline(MessageIotMessage):
    """设备上线"""
    NAME = IOT_MESSAGE_SENSOR_DEVICE_ONLINE

    def __init__(self):
        MessageIotMessage.__init__(self, self.NAME)
        self.sensor_type = 0
        self.sensor_id = 0

class IotMessageSensorDeviceOffline(MessageIotMessage):
    """设备离线"""
    NAME = IOT_MESSAGE_SENSOR_DEVICE_OFFLINE

    def __init__(self):
        MessageIotMessage.__init__(self, self.NAME)
        self.sensor_type = 0
        self.sensor_id = 0

class IotMessageSensorDeviceStatusReport(MessageIotMessage):
    """设备状态上报"""
    NAME = IOT_MESSAGE_SENSOR_DEVICE_STATUS_REPORT
    def __init__(self):
        MessageIotMessage.__init__(self, self.NAME)
        self.sensor_id = ''
        self.sensor_type = ''
        self.service_id = ''
        self.status_data = ''

class IotMessageDeviceCommand(MessageIotMessage):
    """设备控制下行"""
    NAME = IOT_MESSAGE_DEVICE_COMMAND
    def __init__(self):
        MessageIotMessage.__init__(self, self.NAME)
        self.sensor_id = ''
        self.sensor_type = ''
        self.service_id = ''
        self.method = ''
        self.content = ''


MessageClsDict ={}

def registerMessageObject(msgcls):
    MessageClsDict[msgcls.NAME] = msgcls


for key,value in locals().items():
    if key.find('Message')==0 and key not in ('IotMessage','MessageClsDict','Message','MessageType','MessageSplitter'):
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

