#coding:utf-8

import json
from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.timeutils import timestamp_current,current_datetime_string

from mantis.fundamental.utils.timeutils import str_to_timestamp,timestamp_current
from mantis.fanbei.smarthome import constants
from mantis.fanbei.smarthome import model
import iot_message

class IotController(object):
    def __init__(self,adapter):
        self.adapter = adapter
        self.device_id = adapter.device_id
        self.device_iot_channel = None  # 发送到绿城家的通道
        self.profile = ''

    def onActive(self):
        address = constants.DeviceChannelPubIoT.format(device_id=self.device_id)
        broker = instance.messageBrokerManager.get('redis')
        self.device_iot_channel = broker.createPubsubChannel(address)
        self.device_iot_channel.open()

        # 通知华为iot 设备已上线
        message = iot_message.IotMessageDeviceOnline()
        message.device_id = self.device_id
        self.device_iot_channel.publish_or_produce(message.marshall(''))

        self.updateDeviceProfile()

    def updateDeviceProfile(self):
        # 得到设备的profile定义
        device = model.SmartDevice.get(id=self.device_id)
        template = model.RoomTemplate.get(id=device.template_id)
        data = template.profile
        self.profile = json.loads( data )
        print 'Load Profile Successful..'

    def onDeviceDisconnected(self):
        # 通知华为iot 设备已离线
        message = iot_message.IotMessageDeviceOffline()
        message.device_id = self.device_id
        if self.device_iot_channel:
            self.device_iot_channel.publish_or_produce(message.marshall(''))

    def postIotMessage(self,message):
        if self.device_iot_channel:
            self.device_iot_channel.publish_or_produce(message.marshall(''))

    def onMessageSensorStatus(self,message):
        """接收来自下方设备发送上来的端设备状态消息
        转换为huawei iot 规格的消息报文，投递到设备
        message : MessageSensorStatus
        """
        for name,value in message.params.items():
            iot = iot_message.IotMessageSensorDeviceStatusReport()
            iot.device_id = self.device_id
            iot.sensor_id = message.sensor_id
            iot.sensor_type = message.sensor_type
            iot.service_id = self.getServiceId(message.sensor_type, name)
            data = dict( value = value)
            iot.status_data = json.dumps( data ) # 构造iot 适配的消息
            self.postIotMessage(iot)

    def getServiceId(self,sensor_type,feature_id):
        """查询端设备类型的feature_id对应的服务名称 , 例如 :  1 => Switch """
        defines = {}
        for item in self.profile["sensor_defines"]:
            defines[ str(item["type"]) ] = item

        features = {} # {id:{..}}
        for name,value in  defines.get(str(sensor_type),{}):
            features[ str(value["id"]) ] = value
            value["service_id"] = name.capitalize() # 加入服务编号 (iot)
        service_id = features.get(feature_id,{}).get('service_id','')
        return service_id

def get_message(data,ctx):
    """
    ctx :{ name, channel }
    """
    message = iot_message.parseMessage( data )
    if not message:
        return
    if not  isinstance(message,iot_message.IotMessageDeviceCommand):
        return

    service = instance.serviceManager.get('main')
    service.traverseDownMessage( message.device_id ,message)