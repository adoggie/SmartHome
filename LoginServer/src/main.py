# coding:utf-8


import os,sys

from mantis.fundamental.application.app import instance
from mantis.fundamental.application.service import BaseService
from mantis.fanbei.smarthome.model import set_database

class MainService(BaseService):
    def __init__(self,name):
        BaseService.__init__(self,name)
        self.logger = instance.getLogger()
        self.servers = {}
        self.command_controllers ={}

    def init(self, cfgs):
        # self.parseOptions()
        BaseService.init(self,**cfgs)
        self.init_database()

    # def setupFanoutAndLogHandler(self):
    #     from mantis.trade.log import TradeServiceLogHandler
    #     self.initFanoutSwitchers(self.cfgs.get('fanout'))
    #     handler = TradeServiceLogHandler(self)
    #     self.logger.addHandler(handler)

    def start(self,block=True):
        BaseService.start(self)

        # TradeService.start(self)
        # for server in self.servers:
        #     server.start()
        # self.initCommandController()

    def stop(self):
        BaseService.stop(self)

    def initCommandChannels(self):
        pass
        # BaseService.initCommandChannels(self)
        # channel = self.createServiceCommandChannel(CommandChannelTradeAdapterLauncherSub,open=True)
        # self.registerCommandChannel('trade_adapter_launcher',channel)

    def init_database(self):
        conn = instance.datasourceManager.get('mongodb').conn
        db = conn['SmartHome']
        set_database(db)
        return db


