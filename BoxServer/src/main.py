# coding:utf-8

"""
smartbox智能主机接入服务器

"""

import sys
from optparse import OptionParser

from mantis.fundamental.utils.useful import singleton
from mantis.fundamental.application.app import instance
from mantis.fundamental.network.socketutils import Server
from mantis.fundamental.application.service import BaseService
from mantis.fundamental.utils.importutils import import_class

from mantis.fanbei.smarthome import model
from mantis.fanbei.smarthome.message import  *
from mantis.fanbei.smarthome.model import set_database
# from handlers import iot_message

class MainService(BaseService):
    def __init__(self,name):
        BaseService.__init__(self,name)
        self.logger = instance.getLogger()
        self.servers = {}
        self.adapters ={}

        self.apps = {}      # app 软件连接进入

        # self.iot_chan =  None  # 接收绿城+的命令控制
        # self.ctrl_chan = None       # 设备控制消息

    def init(self, kwargs):
        # self.parseOptions()
        BaseService.init(self,**kwargs)
        self.init_database()

        for svrcfg in self.cfgs.get('servers',[]):
            if not svrcfg.get('enable',False):
                self.logger.info("server:{} skipped..".format(svrcfg.get('name')))
                continue
            cls = import_class(svrcfg.get('handler_cls',{}).get('class'))
            # handler = cls()
            # handler.init(**svrcfg.get('handler',{}))

            svrcfg['handler_cls_kwargs'] = svrcfg.get('handler_cls',{}).get('kwargs',{})
            svrcfg['handler_cls'] = cls
            server = Server().init(**svrcfg)
            self.servers[server.name] = server

    def init_database(self):
        conn = instance.datasourceManager.get('mongodb').conn
        db = conn['SmartHome']
        set_database(db)
        return db


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
        # from mantis.trade.log import TradeServiceLogHandler
        self.initFanoutSwitchers(self.cfgs.get('fanout'))
        # handler = TradeServiceLogHandler(self)
        # self.logger.addHandler(handler)

    def start(self,block=True):
        BaseService.start(self)
        for server in self.servers.values():
            server.start()

    def stop(self):
        BaseService.stop(self)

    def initCommandChannels(self):
        BaseService.initCommandChannels(self)

    def getActivedDevices(self):
        return self.adapters.values()

    def deviceOnline(self, adapter):
        """设备上线"""
        self.adapters[adapter.device_id] = adapter

    def deviceOffline(self,adapter):
        """设备离线"""
        for device_id,item in self.adapters.items():
            if item == adapter:
                del self.adapters[device_id]
                break

    def appOnline(self,app):
        self.apps[ app.app_id] = app

    def appOffline(self,app):
        for app_id,item in self.apps.items():
            if item == app:
                del self.adapters[app_id]
                break


"""
Redis
设备最新的位置、报警、心跳时间

Mongodb
各种运行、配置、日志信息 

Redis-Queue/Publish
消息推送、 设备在线命令推送

"""