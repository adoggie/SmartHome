#coding:utf-8

import json
import time, os,os.path,datetime
import traceback
import gevent
from gevent.queue import Queue

from mantis.fundamental.application.app import instance
from mantis.fundamental.utils.timeutils import timestamp_current,current_datetime_string

from mantis.fundamental.utils.timeutils import str_to_timestamp,timestamp_current
from mantis.fundamental.network.socketutils import ConnectionEventHandler
from mantis.fundamental.network.accumulator import JsonDataAccumulator
from mantis.fanbei.smarthome.message import *
from mantis.fanbei.smarthome import constants
from mantis.fanbei.smarthome import model
import iot_message
import iot

class SmartAdapter(ConnectionEventHandler):
    def __init__(self):
        ConnectionEventHandler.__init__(self)
        self.cfgs = {}
        self.accumulator = JsonDataAccumulator()

        self.conn = None
        self.session = None

        self.service = instance.serviceManager.get('main')
        self.mongo = instance.datasourceManager.get('mongodb').conn
        self.redis = instance.datasourceManager.get('redis').conn

        self.raw_file = None
        self.active = False  # 设备是否在线登录
        self.start_time = datetime.datetime.now()
        self.device_id = None
        self.redis = None
        self.device = None
        self.logger = None
        self.seq_gen = None  # RedisIdGenerator().init('')
        self.packet_sequence = 0

        # self.device_iot_channel = None  # 发送到绿城家的通道
        self.iot_controller = None

        self.device_app_pub_channel = None
        self.command_controller = None
        self.queue = Queue()
        self.running = True
        self.peer_address = ''
        self.last_heartbeat = 0
        # self.msg_codec = MessageJsonStreamCodec()
        self.box = None
        self.device_type = ''

    def init(self,**kwargs):
        self.cfgs.update(kwargs)
        self.redis = instance.datasourceManager.get('redis').conn
        self.logger = instance.getLogger()
        # self.seq_gen = RedisIdGenerator().init(self.cfgs.get('sequence_key'))

        # cls = import_class(self.cfgs.get('command_controller'))
        # self.command_controller = cls()
        gevent.spawn(self.messageProcessTask)

    def onConnected(self,conn,address):
        """连接上来"""
        self.logger.debug('device connected .  {}'.format(str(address)))
        self.conn = conn
        self.peer_address = address  # 连接上来的对方地址
        self.last_heartbeat = timestamp_current()

    def onDisconnected(self,conn):
        self.logger.debug('device  disconnected. {} {}'.format(self.device_type, self.device_id))
        self.active = False
        # self.raw_file.close()
        self.service.deviceOffline(self)
        self.running = False

        # 断开连接删除设备与接入服务器的映射
        self.redis.delete(constants.DeviceServerRel.format(self.device_id))

        if self.iot_controller:
            self.iot_controller.onDeviceDisconnected()



    def onData(self,conn,data):
        self.logger.debug("device data retrieve in . {} {}".format(self.device_id, self.device_type))
        json_text_list = self.accumulator.enqueue(data)

        # dump = self.hex_dump(bytes)
        # self.logger.debug("<< "+dump)
        # self.dump_hex_data(dump)

        for text in json_text_list:
            message = parseMessage(text)
            if message:
                self.queue.put([message, current_datetime_string()])

    def checkLogin(self,message):
        from mantis.fanbei.smarthome.token import device_token_check

        device = model.SmartDevice.get(id = message.device_id)
        if not device :
            return False
        secret = device.secret_key
        data = device_token_check(message.token,secret)
        if not data:
            return False
        auth_time = data.get('auth_time',0)
        self.device_id = data.get('id')
        self.device_type = data.get('type')
        TOKEN_VALID_TIME = self.service.getConfig().get('token_valid_time',300)
        # 校验token是否已过期
        if timestamp_current() - auth_time > TOKEN_VALID_TIME:
            instance.getLogger().error(u'过期无效token: ',message.token)
            return False

        return True

    def handleMessage(self,message):
        """ 处理来自设备上行的消息
        """
        # self.logger.debug( str( message.__class__ ))
        self.logger.debug('{} conn:{}'.format(str(self),str(self.conn)))
        # self.logger.debug(message.__class__.__name__+' device_type:{} device_id:{} message type:0x{:02x} '.format(self.device_type,self.device_id,message.Type.value))
        # self.logger.debug(
        #     message.__class__.__name__ + ' device_type:{} device_id:{} content: {} '.format(self.device_type,
        #                                                                                               self.device_id,
        #                                                                                               message.dict()))
        if isinstance(message,MessageHeartBeat):
            return self.handleHeartbeat(message)

        if not self.active: # 设备未登陆
            if isinstance(message, MessageLogin): # 设备注册包
                if not self.checkLogin( message ):
                    self.logger.error('Login Info Check Failed.')
                    self.close()
                    return
                self.onActive() # 设备登陆注册
            else:
                self.logger.error('Device should Login first, socket connection dropped')
                self.close()
                return

        message.device_id = self.device_id
        # message.device_type = self.device_type

        self.postMessageIoT(message)  # 将设备信息分发到 绿城+SDK --> iot

        # if isinstance(message,MessageHeartBeat):
        #     self.handleHeartbeat(message)

        if isinstance(message,MessageDeviceStatus):
            self.handleDeviceStatus(message)

        if isinstance(message,MessageSensorStatus):
            self.handleSensorStatus(message)

        if isinstance(message,MessageDeviceLogInfo):
            self.handleDeviceLogInfo(message)

    def handleDeviceStatus(self,message = MessageDeviceStatus()):
        """ 注意： 包括 家庭模式 """
        import base64
        profile = message.params.get('profile','')
        if profile:
            profile = base64.decodestring(profile)
            self.device.profile = profile
            self.device.save()
            return

        self.device.assign(message.values())
        self.device.alive_time = timestamp_current()
        self.device.save()

        # 写入 redis
        name = constants.DeviceStatusHash.format(self.device_id)
        data = hash_object(self.device)
        self.redis.hmset(name,data)

        # 写入日志
        log = model.LogDeviceStatus()
        log.device_id = self.device_id
        log.sys_time = timestamp_current()
        log.assign(message.params)
        # log.host_ver = message.host_ver
        # log.mcu_ver = message.mcu_ver
        # log.status_time = message.status_time
        # log.boot_time = message.boot_time
        log.save()

    def handleSensorStatus(self,message = MessageSensorStatus()):
        # 写入 redis 记录设备当前最新的状态值
        name = constants.SensorStatusHash.format(device_id=self.device_id,sensor_type=message.sensor_type,sensor_id=message.sensor_id)
        data = message.params
        self.redis.hmset(name,data)

        self.iot_controller.onMessageSensorStatus( message )

        # 写入日志
        log = model.LogSensorStatus()
        log.device_id = self.device_id
        log.sys_time = timestamp_current()
        log.sensor_id = message.sensor_id
        log.sensor_type = message.sensor_type
        log.assign(message.params)
        # log.params = json.dumps( message.params )
        log.save()

    def handleDeviceLogInfo(self,message = MessageDeviceLogInfo()):
        log = model.LogDeviceLogInfo()
        log.device_id = self.device_id
        log.sys_time = timestamp_current()
        log.device_time = message.time
        log.content = message.content
        log.save()

    def handleHeartbeat(self,message):
        self.last_heartbeat = timestamp_current()

        # bytes = message.response()
        # self.conn.sendData(bytes)
        #
        # # 更新设备最新的状态和位置信息到Redis
        # data = message.dict()
        # self.update_device_in_cache(data)


    def postMessageIoT(self,message):
        # 设备登陆上线和状态需发送给绿城+ SDK
        if not isinstance(message,(MessageSensorStatus,MessageLogin)):
            return

        m =  None
        if isinstance(message,MessageSensorStatus):
            m = iot_message.MessageSensorStatus()
            m.device_id = message.device_id
            m.sensor_id = message.sensor_id
            m.sensor_type = message.sensor_type
            m.params = message.params
        if m:
            self.device_iot_channel.publish_or_produce( message.marshall('') )

        # # 写入日志数据库
        # dbname = 'ismart_device_log'
        # coll = self.mongo[dbname][self.device_id]
        # coll.insert_one(data)

    def open(self):
        pass

    def setConnection(self,sock_conn):
        self.conn = sock_conn

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()


    def make_rawfile(self):
        fmt = '%Y%m%d_%H%M%S.%f'
        ts = time.time()
        name = time.strftime(fmt, time.localtime(ts)) + '.raw'
        name = os.path.join(instance.getDataPath(),name)
        self.raw_file = open(name,'w')


    def hex_dump(self,bytes):
        dump = ' '.join(map(lambda _:'%02x'%_, map(ord, bytes)))
        return dump


    def threadHeartbeat(self):
        """定时发送设备的心跳包"""
        sleep = self.cfgs.get('heartbeat', 10)
        while self.running:
            gevent.sleep( sleep )
            self.traverseDown(MessageHeartBeat())



    def onActive(self):
        """设备在线登录了"""
        self.logger.debug('device onActive. {} {}'.format(self.device_type, self.device_id))
        self.active = True
        gevent.spawn(self.threadHeartbeat)  # 定时心跳发送

        access_url = self.service.getConfig().get('access_api_url')     #暴露给外部调用的web接口，接收命令控制
        self.redis.set( constants.DeviceAccessHttpAPI.format(self.device_id),access_url)

        # 记录设备由哪个sever接入的
        # service_id = self.service.getConfig().get('id')
        # self.redis.hset(constants.DeviceServerRel,self.device_id,service_id)

        device = model.SmartDevice.get(id = self.device_id)
        if device:
            self.device = device
        else:
            self.logger.error('device not register',self.device_id)
            self.close()
            return

        CHECK_ACTIVE = False
        if CHECK_ACTIVE:
            if not device.active_time:  # 未激活
                self.logger.error('device not actived.',self.device_id)
                self.close()
                return

        device.alive_time = timestamp_current()
        device.save()

        self.service.deviceOnline(self)

        # 创建到华为iot的通道
        self.iot_controller = iot.IotController(self)
        self.iot_controller.onActive()

        # 设备上线，即刻发送设备状态查询
        self.traverseDown(MessageDeviceStatusQuery())


    def traverseDown(self,message):
        """转发设备下行消息"""
        self.conn.sendData(message.marshall())

        if isinstance(message, MessageDeviceValueSet):
            log = model.LogDeviceValueSet()
            log.device_id = self.device_id
            log.sys_time = timestamp_current()
            log.param_name = message.param_name
            log.param_value = message.param_value
            log.save()

        if isinstance(message, MessageSensorValueSet):
            log = model.LogSensorValueSet()
            log.device_id = self.device_id
            log.sensor_id = message.sensor_id
            log.sensor_type = message.sensor_type
            log.sys_time = timestamp_current()
            log.param_name = message.param_name
            log.param_value = message.param_value
            log.save()

    def messageProcessTask(self):
        """处理设备上报消息的工作队列"""
        while self.running:
            # 长久没有心跳包
            if timestamp_current() - self.last_heartbeat > 60*5:
                self.logger.warn('Heartbeat Lost. Close socket. {} {} '.format(self.device_id, self.device_type))
                self.close()
                break
            try:
                message,date = self.queue.get(block=True, timeout=1)
                try:
                    self.logger.debug('message pop from queue: {} {}  {} {}'.format(date,message.__class__.__name__,self.device_id,self.device_type))

                    self.handleMessage(message)
                except:
                    self.logger.warn(traceback.print_exc())
                    self.close()
                    break
            except:pass

        self.logger.warn('messageTask() exiting.. {} {} '.format(self.device_id, self.device_type))




