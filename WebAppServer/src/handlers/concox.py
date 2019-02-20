#coding:utf-8

import json
import time,datetime,os,os.path
import gevent
from mantis.fundamental.application.app import instance
from vendor.concox.message import *

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

    def setAccumulator(self,acc):
        self.accumulator = acc


    def handle(self,message):
        """
        接收到设备标识信息时，需要设置 socket conn的标识属性
        if message isinstance MessageLogin:
            self.conn.client_id.unique_id = message.imei
        """
        if not self.active:
            if isinstance(message, MessageLogin):
                self.device_id = message.device_id
                bytes = message.response()
                self.conn.sendData(bytes)
                self.onActive()
            else:
                return

        data = message.dict()
        data['name'] = message.__name__
        data['type_id'] = message.Type.value
        data['type_comment'] = message.Type.comment
        #将设备消息发布出去
        self.service.dataFanout('switch0',json.dumps(data))
        # 写入日志数据库
        dbname = 'concox_device_log'
        coll = self.mongo[dbname][self.device_id]
        coll.insert_one(data)







    def init(self,cfgs):
        self.cfgs = cfgs
        return self

    def open(self):
        pass

    def setConnection(self,sock_conn):
        self.conn = sock_conn

    def close(self):
        pass

    def onConnected(self,sock_con):
        self.setConnection(sock_con)
        self.make_rawfile()

    def make_rawfile(self):
        fmt = '%Y%m%d_%H%M%S.%f'
        ts = time.time()
        name = time.strftime(fmt, time.localtime(ts)) + '.raw'
        name = os.path.join(instance.getDataPath(),name)
        self.raw_file = open(name,'w')

    def onDisconnected(self):
        self.active = False
        self.raw_file.close()

    def onData(self,bytes):
        """ raw data """
        messages = self.accumulator.enqueue(bytes)
        for message in messages:
            self.handle(message)

        self.raw_file.write(bytes)
        self.raw_file.flush()

    def onActive(self):
        """设备在线登录了"""
        self.active = True
        # 启动命令发送任务，读取下发命令
        gevent.spawn(self.commandTask)

    def commandTask(self):
        """从redis中读取设备的命令，并进行发送到设备"""
        key = 'deivce.command.queue.{}'.format(self.device_id)
        while self.active:
            data = self.redis.blpop(key,1)
            if data:
                self.conn.sendData(data)




