# coding:utf-8


import sys
from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.application.app import instance
from mantis.trade.service import TradeService
from optparse import OptionParser
from server import Server
from mantis.BlueEarth.vendor.concox.gt03.packet import NetWorkPacketAllocator
# from mantis.BlueEarth.vendor.concox.gt03.message import MessageOnlineCommandAllocator
from mantis.BlueEarth.constants import *
from mantis.BlueEarth import model
from mantis.BlueEarth.utils import sendCommand


class MainService(TradeService):
    def __init__(self,name):
        TradeService.__init__(self,name)
        self.logger = instance.getLogger()
        self.servers = {}
        self.adapters ={}

    def init(self, cfgs,**kwargs):
        # self.parseOptions()
        super(MainService,self).init(cfgs)
        for svrcfg in self.cfgs.get('servers',[]):
            if not svrcfg.get('enable',False):
                self.logger.info("server:{} skipped..".format(svrcfg.get('name')))
                continue
            server = Server().init(svrcfg)
            self.servers[server.name] = server
        # generator = RedisIdGenerator().init(DeviceSequence)
        # NetWorkPacketAllocator().setSequenceGenerator(generator)
        # MessageOnlineCommandAllocator().setSequenceGeneroator(generator)


    def get_database(self):
        conn = instance.datasourceManager.get('mongodb').conn
        return conn['BlueEarth']


    def parseOptions(self):
        command = ''
        if len(sys.argv) < 2:
            print 'Error: Command Must Be (CREATE,LIST,PULL,UPLOAD,REMOVE AND RUN ).'
            raise RuntimeError()
        command = sys.argv[1].lower()
        if command not in ('create','list','pull','upload','remove','run'):
            return False

        parser = OptionParser()
        parser.add_option("--user",dest='user')
        parser.add_option("--remote",action='store_false',dest='isremote')   # 策略编号

        parser.add_option("--launcher_id",dest='launcher') # 加载器编号
        args = sys.argv[2:]
        (options, args) = parser.parse_args(args)
        if len(args)==0:
            print 'Error: strategy name missed.'
            return False

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self,block=True):
        TradeService.start(self)
        for server in self.servers.values():
            server.start()

    def stop(self):
        TradeService.stop(self)

    def initCommandChannels(self):
        TradeService.initCommandChannels(self)
        # channel = self.createServiceCommandChannel(CommandChannelTradeAdapterLauncherSub,open=True)
        # self.registerCommandChannel('trade_adapter_launcher',channel)

    def getActivedDevices(self):
        return self.adapters.values()

    def deviceOnline(self,adatper):
        self.adapters[adatper.device_id] = adatper

    def deviceOffline(self,adapter):
        for device_id,item in self.adapters.items():
            if item == adapter:
                del self.adapters[device_id]
                break

        # if self.adapters.has_key(adapter.device_id):
        #     del self.adapters[adapter.device_id]

    def sendCommand(self,device_id,command,online=False):
        """将命令推入发送队列，待设备上线，统一发送"""
        device = model.Device.get(device_id=device_id)
        if not device:
            self.logger.error('device_id:{} is not existed.'.format(device_id))
            return
        device_type = device.device_type
        # adapter = self.adapters.get(device_id)
        # if not adapter:
        #     self.logger.error('Method:sendCommand Detail: device_id({}) is not found.'.format(device_id))
        #     return False
        if online: # 必须在线发送
            if not self.adapters.has_key(device_id):
                self.logger.debug('sendCommand Error,device not online. {}'.format(device_id))
                return
        sendCommand(device_id,device_type,command)
        return True

    # def onMessage(self,message,adapter):
    #     """
    #     """


"""
Redis
设备最新的位置、报警、心跳时间

Mongodb
各种运行、配置、日志信息 

Redis-Queue/Publish
消息推送、 设备在线命令推送

"""