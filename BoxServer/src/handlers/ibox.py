#coding:utf-8

import json
import time, os,os.path,datetime
import gevent
from gevent.queue import Queue
from mantis.fundamental.application.app import instance
from mantis.iSmart.constants import *
from mantis.fundamental.utils.timeutils import timestamp_current,current_datetime_string
from mantis.iSmart import model
from mantis.iSmart.utils import RedisIdGenerator
from mantis.fundamental.utils.importutils import import_class
from mantis.iSmart.codec import MessageJsonStreamCodec
from mantis.iSmart.message import *
from mantis.fundamental.utils.timeutils import str_to_timestamp,timestamp_current

class DataAdapter(object):
    """处理设备上传消息的应用层逻辑"""
    def __init__(self):
        self.cfgs = None
        self.conn = None
        self.session = None
        self.service = instance.serviceManager.get('main')
        self.mongo = instance.datasourceManager.get('mongodb').conn
        self.redis = instance.datasourceManager.get('redis').conn
        self.accumulator = None
        self.raw_file = None
        self.active = False  # 设备是否在线登录
        self.start_time = datetime.datetime.now()
        self.device_id = None
        self.redis = None
        self.obj = None
        self.logger = None
        self.seq_gen = None #RedisIdGenerator().init('')
        self.packet_sequence = 0
        self.device_pub_channel = None
        self.device_app_pub_channel = None
        self.command_controller = None
        self.queue = Queue()
        self.running = True
        self.peer_address = ''
        self.last_heartbeat = 0
        self.msg_codec = MessageJsonStreamCodec()
        self.box = None

    def next_packet_sequence(self):
        self.packet_sequence+=1
        if self.packet_sequence >= 0x8000:
            self.packet_sequence = 1
        return self.packet_sequence

    @property
    def device_type(self):
        return self.cfgs.get('device_type')

    def setAccumulator(self,acc):
        self.accumulator = acc

    def handle(self,message):
        """
        """
        # self.logger.debug( str( message.__class__ ))
        self.logger.debug('{} conn:{}'.format(str(self),str(self.conn)))
        self.logger.debug(message.__class__.__name__+' device_type:{} device_id:{} message type:0x{:02x} '.format(self.device_type,self.device_id,message.Type.value))
        self.logger.debug(
            message.__class__.__name__ + ' device_type:{} device_id:{} content: {} '.format(self.device_type,
                                                                                                      self.device_id,
                                                                                                      message.dict()))
        if not self.active:
            if isinstance(message, MessageBoxRegister): # 设备注册包
                self.device_id = message.box.device_id
                self.box = message.box
                self.onActive()
            else:
                self.logger.error('first message is not MessageLogin, destroy socket connection.')
                self.close()
                # return

        message.device_id = self.device_id
        message.device_type = self.device_type

        self.distribute_message(message)

        if isinstance(message,MessageHeartbeat):
            self.last_heartbeat = timestamp_current()
            self.handle_heartbeat(message)

        if isinstance(message,MessageProbeStatus):
            pass

        if isinstance(message,MessageProbeAlarm):
            pass

    def handle_heartbeat(self,message):
        bytes = message.response()
        self.conn.sendData(bytes)

        # 更新设备最新的状态和位置信息到Redis
        data = message.dict()
        self.update_device_in_cache(data)


    def distribute_message(self,message):
        data = message.dict()

        data['name'] = message.__class__.__name__
        # data['type_id'] = message.Type.value
        # data['type_comment'] = message.Type.comment
        data['timestamp'] = timestamp_current()
        data['datetime'] = current_datetime_string()
        data['device_id'] = self.box.device_id
        data['device_type'] = self.box.category

        # if data.has_key('extra'): del data['extra']
        # if data.has_key('Type'): del data['Type']

        print data
        #将设备消息发布出去
        self.service.dataFanout('switch0',json.dumps(data))

        # 发布到隶属于设备编号的通道上去
        self.device_pub_channel.publish_or_produce(json.dumps(data))

        # # 写入日志数据库
        dbname = 'ismart_device_log'
        coll = self.mongo[dbname][self.device_id]
        coll.insert_one(data)

    def init(self,cfgs):
        self.cfgs = cfgs
        self.redis = instance.datasourceManager.get('redis').conn
        self.logger = instance.getLogger()
        self.seq_gen = RedisIdGenerator().init(self.cfgs.get('sequence_key'))

        cls = import_class(self.cfgs.get('command_controller'))
        self.command_controller = cls()
        gevent.spawn(self.messageTask)
        return self

    def open(self):
        pass

    def setConnection(self,sock_conn):
        self.conn = sock_conn

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()

    def onConnected(self,sock_con,address,*args):
        """连接上来"""
        self.logger.debug('device connected .  {}'.format(str(address)))
        self.setConnection(sock_con)
        self.peer_address = address # 连接上来的对方地址
        self.last_heartbeat = timestamp_current()

        # self.make_rawfile()

    def make_rawfile(self):
        fmt = '%Y%m%d_%H%M%S.%f'
        ts = time.time()
        name = time.strftime(fmt, time.localtime(ts)) + '.raw'
        name = os.path.join(instance.getDataPath(),name)
        self.raw_file = open(name,'w')

    def onDisconnected(self):
        self.logger.debug('device  disconnected. {} {}'.format(self.device_type,self.device_id))
        self.active = False
        # self.raw_file.close()
        self.service.deviceOffline(self)
        self.running = False

        # 断开连接删除设备与接入服务器的映射
        self.redis.delete(DeviceLandingServerKey.format(self.device_id))

    def hex_dump(self,bytes):
        dump = ' '.join(map(lambda _:'%02x'%_, map(ord, bytes)))
        return dump


    def onData(self,bytes):
        """ raw data """
        self.logger.debug("device data retrieve in . {} {}".format(self.device_id,self.device_type))
        # dump = self.hex_dump(bytes)
        # self.logger.debug("<< "+dump)
        # self.dump_hex_data(dump)
        messages = self.msg_codec.decode(bytes)

        for message in messages:
            self.queue.put([message,current_datetime_string()])

    def onActive(self):
        """设备在线登录了"""
        self.logger.debug('device onActive. {} {}'.format(self.device_type, self.device_id))

        self.active = True
        # 启动命令发送任务，读取下发命令
        gevent.spawn(self.commandTask)


        access_url = self.service.getConfig().get('access_command_url')
        self.redis.set(DeviceLandingServerKey.format(self.device_id),access_url)


        self.redis.hset(DeviceActiveListKeyHash,self.device_id,timestamp_current())
        obj = model.Device.get(device_id = self.device_id)
        if obj:
            self.obj = obj
        else:
            self.logger.debug('device: {} not found in database.'.format(self.device_id))

        self.service.deviceOnline(self)

        # 创建通道
        address = DeviceChannelPub.format(device_id=self.device_id)
        broker = instance.messageBrokerManager.get('redis')
        self.device_pub_channel = broker.createPubsubChannel(address)
        self.device_pub_channel.open()

        # 创建应用通道
        address = DeviceAppChannelPub.format(device_id=self.device_id)
        broker = instance.messageBrokerManager.get('redis')
        self.device_app_pub_channel = broker.createPubsubChannel(address)
        self.device_app_pub_channel.open()

        # 查询一次设备运行配置信息
        # self.queryDeviceConfig()

    def queryDeviceConfig(self):
        """一次查询设备所有运行配置参数"""
        from mantis.BlueEarth.utils import sendCommand
        cmds = self.command_controller.init_commands()
        for cmd in cmds:
            sendCommand(self.device_id,self.device_type,cmd)

    def commandTask(self):
        """从redis中读取设备的命令，并进行发送到设备"""
        key = DeviceCommandQueue.format(device_type = self.device_type,device_id = self.device_id)
        while self.active:
            data = self.redis.blpop(key,1)
            if data:
                key,content = data
                if not content:
                    continue

                if not self.sendCommand(content):
                    break
        self.logger.debug('commandTask Exiting.. {} {}'.format(self.device_type, self.device_id))

    def sendCommand(self,command):

        content = command
        content = self.command_controller.execute(content)
        if not content:
            return True

        self.logger.debug('SendCommand: {} {} {}'.format(content,self.device_id,self.device_type))
        command = MessageOnlineCommand()
        command.content = content
        command.sequence = self.seq_gen.next_id()
        packet = command.packet()
        packet.sequence = self.next_packet_sequence()
        try:
            self.conn.sendData(packet.to_bytes())
        except:
            self.logger.error('socket sendData error. {} {} {}'.format(content,self.device_id,self.device_type))
            self.close()
            return False
        # save send record
        send = model.CommandSend()
        send.device_id = self.device_id
        send.send_time = timestamp_current()
        send.sequence = packet.sequence
        send.command = command.content
        send.save()
        return True
        # self.logger.debug('commandTask Exiting.. {} {}'.format(self.device_type, self.device_id))


    def messageTask(self):
        import traceback

        while self.running:
            # 长久没有心跳包
            if timestamp_current() - self.last_heartbeat > MaxLiveTimeDeviceLandingServerKey:
                self.logger.warn('device heartbeat timer reached limit. close socket. {} {} '.format(self.device_id, self.device_type))
                self.close()
                break
            try:
                message,date = self.queue.get(block=True, timeout=1)
                try:
                    self.logger.debug('message pop from queue: {} {}  {} {}'.format(date,message.__class__.__name__,self.device_id,self.device_type))
                    self.handle(message)
                except:
                    self.logger.warn(traceback.print_exc())
            except:pass

        self.logger.warn('messageTask() exiting.. {} {} '.format(self.device_id, self.device_type))




