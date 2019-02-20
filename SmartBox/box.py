#coding:utf-8
import mantis.iSmart.codec as codec
from mantis.iSmart.message import *
from mantis.iSmart.types import BoxControllerInfo
from mantis.fundamental.utils.useful import hash_object
from mantis.fundamental.utils.useful import singleton

import threading
import time
import socket,select




@singleton
class BoxController(object):
    """设备控制器"""
    def __init__(self):
        self.cfgs = {}
        self.work_thread = threading.Thread(target=self.workTask)
        self.sock_thread = threading.Thread(target=self.sockRead)
        self.heartbeat = 0
        self.device = None
        self.running = False
        self.sock = None
        self.codec = codec.MessageJsonStreamCodec()
        self.box_info = BoxControllerInfo()
        self.probe_list = {}

    def initSocket(self):
        """连接服务器"""
        pass

    def reConnectHost(self):
        if self.sock:
            return self.sock
        cfgs = self.cfgs.get('server')
        host = cfgs.get('host')
        port = cfgs.get('port')
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            sock.connect((host,int(port)))
            self.sock = sock
            self.sock_thread.start()
        except:
            return None

        return self.sock

    def sockRead(self):
        self.onConnected()
        while self.running:
            data = self.sock.recv(1000)
            if data:
                self.onData(data)
        self.codec.reset()
        self.onDisconnected()
        self.sock = None

    def onConnected(self):
        """发送box注册信息"""
        msg = MessageBoxRegister()
        box = BoxControllerInfo()
        msg.box = box
        data = msg.dict()
        self.sendData(data)

    def onDisconnected(self):
        pass

    def onData(self,data):
        """socket 链路数据接收解析出 json报文"""
        msg_list = self.codec.decode(data)
        for msg in msg_list:
            self.onMessage(msg)

    def onMessage(self,msg):
        """消息解析"""
        message  = msg.get('message')
        if  message == MessageType.UP_ENDPOINT_HEARTBEAT:
            self.onProbeHeartbeat(msg)
        if message == MessageType.UP_ENDPOINT_STATUS_REPORT:
            self.onProbeStatus(msg)
        if message == MessageType.UP_ENDPOINT_ALARM:
            self.onProbeAlarm(msg)
        if message == MessageType.UP_ENDPOINT_REGISTER:
            self.onProbeRegister(msg)

    def onProbeHeartbeat(self,msg):
        pass

    def onProbeStatus(self,msg):
        msg['box'] = hash_object(self.box_info)
        self.sendUpStreamData(msg)

    def onProbeAlarm(self,msg):
        pass

    def onProbeRegister(self,msg):
        pass

    def onCommandControl(self,msg):
        """主机控制命令下发"""
        pass

    def onCommandStatusQuery(self,msg):
        """主机下发状态查询命令"""
        pass

    def init(self,cfgs):
        self.cfgs = cfgs
        box =  self.cfgs.get('box_settings',{})
        object_assign(self.box_info,box)

        return self

    def open(self,**cfgs):
        """
        cfgs:
            heartbeat : 5 默认5秒发送心跳 ， 0 : 不可用
            host: 服务器ip
            port: 服务器端口
        """
        self.running = True


    def close(self):
        self.running = False

    def sendUpStreamData(self,data):
        if self.reConnectHost():
            data = self.codec.encode(data)
            self.sock.sendall(data)

    def workTask(self):
        last_tick = time.time()
        while self.running:
            if time.time() - last_tick > self.heartbeat:
                self.onHeartbeat()
                last_tick = time.time()

    def run(self):
        self.sock_thread.join()
        self.work_thread.join()
