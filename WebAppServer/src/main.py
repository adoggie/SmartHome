# coding:utf-8


import os,sys
from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.application.app import instance
from mantis.trade.service import TradeService,TradeFrontServiceTraits,ServiceType,ServiceCommonProperty
from optparse import OptionParser
from mantis.fundamental.utils.importutils import import_class
from mantis.BlueEarth.utils import sendCommand

class MainService(TradeService):
    def __init__(self,name):
        TradeService.__init__(self,name)
        self.logger = instance.getLogger()
        self.servers = {}
        self.command_controllers ={}



    def init(self, cfgs,**kwargs):
        # self.parseOptions()
        super(MainService,self).init(cfgs)

    def setupFanoutAndLogHandler(self):
        from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        handler = TradeServiceLogHandler(self)
        self.logger.addHandler(handler)

    def start(self,block=True):
        # TradeService.start(self)
        # for server in self.servers:
        #     server.start()
        self.initCommandController()

    def stop(self):
        TradeService.stop(self)

    def initCommandChannels(self):
        TradeService.initCommandChannels(self)
        # channel = self.createServiceCommandChannel(CommandChannelTradeAdapterLauncherSub,open=True)
        # self.registerCommandChannel('trade_adapter_launcher',channel)

    def sendCommand(self,device_id,command):
        """
        在线设备即刻发送，离线设备寄存发送命令

        """
        from mantis.BlueEarth import model
        device = model.Device.get(device_id=device_id)
        if not device:
            self.logger.error('device_id:{} is not existed.'.format(device_id))
            return
        device_type = device.device_type
        sendCommand(device_id,device_type,command)

    def sendDownStreamData(self, device_id,data):
        key = 'deivce.command.queue.{}'.format(device_id)
        redis = instance.datasourceManager.get('redis').conn
        redis.rpush(device_id, data)

    def initCommandController(self):
        for item in self.getConfig().get('command_controllers',[]):
            name = item.get('name')
            clsname = item.get('class')
            cls = import_class(clsname)
            controller = cls()
            self.command_controllers[name] = controller

    def getCommandController(self,name):
        return self.command_controllers.get(name)

    def get_database(self):
        conn = instance.datasourceManager.get('mongodb').conn
        return conn['BlueEarth']

    def sendDevicePassword(self,phone,device_id,password,reason=''):
        """用户在找回密码或注册设备时请求密码查询返回"""
        import sms
        # from mantis.BlueEarth.utils import mak
        return sms.send_sms(phone,'shyg','find_device_password',code=password)
