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
# from mantis.fanbei.smarthome.message import *
from mantis.fanbei.smarthome import constants
from mantis.fanbei.smarthome import model

from .message import *

"""
app登录进入，等待app发送订阅subscribe消息。
订阅设备时，启动redis的sub消息订阅，接收设备消息之后发送到接入tcp通道。

"""
class AppAdapter(ConnectionEventHandler):
    """app接入流服务"""
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

        self.device_app_pub_channel = None
        self.command_controller = None
        self.queue = Queue()
        self.running = True
        self.peer_address = ''
        self.last_heartbeat = 0
        # self.msg_codec = MessageJsonStreamCodec()
        self.box = None
        self.device_type = ''
        self.joined = False # 是否已加入

        self.subscribed_ids = {} # 已订阅设备编号
        self.app_id = str(time.time())

    def init(self,**kwargs):
        self.cfgs.update(kwargs)
        self.redis = instance.datasourceManager.get('redis').conn
        self.logger = instance.getLogger()
        gevent.spawn(self.messageProcessTask)

        self.initBroker()

    def onDeviceTraverseUpMessage(self,message,ctx):
        """接收到投递过来的设备状态消息,转发到当前 tcp 通道"""
        from mantis.fanbei.smarthome.message import MessageSensorStatus ,parseMessage
        message = parseMessage(message)

        if not isinstance(message,MessageSensorStatus):
            self.logger.error("Message From Redis is Not MessageSensorStatus.")
            return 
        self.traverseDown(message)


    def initBroker(self):
        self.broker = instance.messageBrokerManager.get('redis')

    def onConnected(self,conn,address):
        """连接上来 ， 等待app发送join请求，超时 10s 断开连接 """
        self.logger.debug('app connected .  {}'.format(str(address)))
        self.conn = conn
        self.peer_address = address  # 连接上来的对方地址
        self.last_heartbeat = timestamp_current()
        # gevent.spawn_later(self.checkLogin,10)
        gevent.spawn(self.checkLogin)

    def checkLogin(self):
        """检查是否已发起订阅"""
        gevent.sleep(100)
        if not self.subscribed_ids :
            print 'App Subscribe Timeout , destroy connection..'
            self.close()

    def onDisconnected(self,conn):
        self.logger.debug('App  disconnected. {} {}'.format(self.device_type, self.device_id))
        self.active = False
        # self.raw_file.close()


        for id,channel in self.subscribed_ids.items():
            # channel = self.subscribed_ids.get(id_)
            if channel:
                channel.close()  # 关闭订阅
                # del self.subscribed_ids[id_]

        self.service.appOffline(self)
        self.running = False
        self.subscribed_ids = {}


    def onData(self,conn,data):
        self.logger.debug("app data retrieve in . "+ data)
        json_text_list = self.accumulator.enqueue(data)

        # dump = self.hex_dump(bytes)
        # self.logger.debug("<< "+dump)
        # self.dump_hex_data(dump)

        for text in json_text_list:
            message = parseMessage(text)
            if message:
                self.queue.put([message, current_datetime_string()])

    def handleMessage(self,message):
        """ 处理来自设备上行的消息
        """

        if isinstance(message,MessageAppHeartbeat):
            return self.handleHeartbeat(message)

        if isinstance(message,MessageAppSubscribe):
            self.handleSubscribe(message)

        if isinstance(message,MessageAppUnSubscribe):
            self.handleUnSubscribe(message)


    def subscribeDevice(self,device_id):
        channelname = constants.DeviceChannelPubTraverseUp.format( device_id = device_id)
        channel = self.broker.createPubsubChannel(channelname, self.onDeviceTraverseUpMessage)
        channel.open()
        return channel

    def getAutchDeviceIds(self,authcode):
        """从redis读取授权的设备编码, 多个设备编码以 , 分隔"""
        name = constants.AppRequestAuthCodeWidthIdsPrefix + authcode
        value = self.redis.get(name)
        ids = str(value).split(',')
        return ids

    def handleSubscribe(self,message):
        # return
        authed_ids = self.getAutchDeviceIds(message.authcode)

        for id_ in message.ids:
            if id_  not in authed_ids:
                continue

            if not self.subscribed_ids.has_key(id_):
                channel = self.subscribeDevice(id_)
                self.subscribed_ids[id_] = channel

    def handleUnSubscribe(self,message):
        for id_ in message.ids:
            channel = self.subscribed_ids.get(id_)
            if channel:
                channel.close()  # 关闭订阅
                del self.subscribed_ids[id_]

    def handleHeartbeat(self,message):
        self.last_heartbeat = timestamp_current()

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


    def traverseDown(self,message):
        """转发设备下行消息"""
        if self.conn:
            self.conn.sendData(message.marshall())


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




