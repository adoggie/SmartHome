#coding:utf-8
import mantis.iSmart.codec as codec
from mantis.iSmart.message import *
from mantis.fundamental.utils.useful import hash_object
import threading
import socket,select
from endpoint import ProbeDeviceInfo


class EndpointDeviceProxy(object):
    def __init__(self):
        self.device = ProbeDeviceInfo()
        self.conn = None
        self.codec = codec.MessageJsonStreamCodec()

class EndpointController(object):
    """设备控制器"""
    def __init__(self):
        self.cfgs = {}
        # self.work_thread = threading.Thread(target=self.workTask)
        self.sock_thread = threading.Thread(target=self.sockSelect)
        self.heartbeat = 0
        self.device = None
        self.running = False
        self.socket = None
        self.codec = codec.MessageJsonStreamCodec()
        self.box_info = None
        self.ep_list = {}

    def initIpcSocket(self):
        self.socket = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        ipc = self.cfgs.get('ipc')
        self.socket.bind(ipc)
        self.socket.listen(5)

        self.sock_thread.start()

    def sockSelect(self):
        rdFds = []
        rdFds.append(self.socket)
        while self.running:
            rFd, wFd, eFd = select.select(rdFds, [], [])
            for fd in rFd:
                if fd is self.socket:
                    conn, addr = self.socket.accept()
                    rdFds.append(conn)
                    print('Connected by', addr)

                    device = EndpointDeviceProxy()
                    device.conn = conn
                    self.ep_list[conn] = device
                else:
                    data = fd.recv(1024)
                    if not data:
                        rdFds.remove(fd)
                        del self.ep_list[fd]
                        fd.close()
                        break
                    proxy = self.ep_list[fd]
                    msg_list = proxy.codec.decode(data)
                    for msg in msg_list:
                        msg['__conn__'] = fd
                        self.onData(msg)
        print 'select serving exit..'

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
        from box import BoxController
        ep = self.getEndpointProxy(msg)
        msg['device'] = hash_object(ep.device)
        BoxController().onProbeStatus(msg)

    def onProbeAlarm(self,msg):
        pass

    def onProbeRegister(self,msg):
        ep = self.getEndpointProxy(msg)
        object_assign( ep.device,msg.get('device'))

    def getEndpointProxy(self,msg):
        conn = msg.get('__conn__')
        ep = self.ep_list.get(conn)
        return ep

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

    def close(self):
        self.running = False


    def sendEndpointData(self,sn,data):
        """忘指定sn的终端设备发送消息"""
        for conn,p in self.ep_list.items():
            if p.device.sn == sn:
                data = p.encode(data)
                conn.sendall(data)

    # def workTask(self):
    #     last_tick = time.time()
    #     while self.running:
    #         if time.time() - last_tick > self.heartbeat:
    #             self.onHeartbeat()
    #             last_tick = time.time()

    def run(self):
        self.sock_thread.join()
        # self.work_thread.join()
