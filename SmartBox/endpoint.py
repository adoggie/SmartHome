#coding:utf-8
import mantis.iSmart.codec as codec
from mantis.iSmart.message import *
from mantis.iSmart.types import ProbeDeviceInfo

from mantis.fundamental.utils.useful import hash_object
import threading
import time
import socket


class EndpointDeviceBase(object):
    """探测设备基类"""
    def __init__(self):
        self.cfgs = {}
        self.work_thread = threading.Thread(target=self.workTask)
        self.sock_thread = threading.Thread(target=self.sockRead)
        self.heartbeat = 0
        self.device = None
        self.running = False
        self.socket = None
        self.codec = codec.MessageJsonStreamCodec()

    def initIpcSocket(self):
        self.socket = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        ipc = self.cfgs.get('ipc')
        self.socket.connect(ipc)
        self.sock_thread.start()

    def sockRead(self):
        while self.running:
            data = self.socket.recv(1000)
            if data:
                self.onData(data)

    def onData(self,data):
        """socket 链路数据接收解析出 json报文"""
        msg_list = self.codec.decode(data)
        for msg in msg_list:
            self.onMessage(msg)

    def onMessage(self,msg):
        """消息解析"""
        if msg.get('message') == MessageType.DOWN_ENDPOINT_QUERY_STATUS:
            self.onCommandStatusQuery(msg)
        if msg.get('message') == MessageType.DOWN_ENDPOINT_CONTROL:
            self.onCommandControl(msg)

    def onCommandControl(self,msg):
        """主机控制命令下发"""
        pass

    def onCommandStatusQuery(self,msg):
        """主机下发状态查询命令"""
        pass

    def open(self,**cfgs):
        """
        cfgs:
            heartbeat : 5 默认5秒发送心跳 ， 0 : 不可用
            ipc: /tmp/ismartbox.sock
        """
        self.running = True
        self.cfgs = cfgs
        self.initIpcSocket()

        self.heartbeat = cfgs.get('heartbeat',0)
        if self.heartbeat:
            self.work_thread.start()

    def close(self):
        self.running = False

    def register(self,device,**cfgs):
        """注册设备信息"""
        self.device = device

        msg = MessageProbeRegister()
        msg.device = self.device
        data = msg.dict()
        self.sendData(data)

    def sendStatus(self,data):
        """发送设备状态"""
        msg = MessageProbeStatus()
        msg.params = data
        self.sendData(msg.dict())

    def sendAlarm(self,data):
        """发送报警"""
        msg = MessageProbeAlarm()
        msg.params = data
        self.sendData(msg.dict())

    def sendData(self,data):
        data = self.codec.encode(data)
        self.socket.sendall(data)

    def onHeartbeat(self):
        self.sendData(MessageHeartbeat().dict())

    def workTask(self):
        last_tick = time.time()
        while self.running:
            if time.time() - last_tick > self.heartbeat:
                self.onHeartbeat()
                last_tick = time.time()

    def run(self):
        self.sock_thread.join()
        self.work_thread.join()
