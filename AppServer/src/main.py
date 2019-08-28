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
from mantis.fanbei.smarthome.constants import DeviceChannelPubTraverseDown,DeviceChannelPubTraverseUp

class MainService(BaseService):
    def __init__(self,name):
        BaseService.__init__(self,name)
        self.logger = instance.getLogger()



    def init(self, kwargs):
        # self.parseOptions()
        BaseService.init(self,**kwargs)
        self.init_database()

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


    def stop(self):
        BaseService.stop(self)

    def initCommandChannels(self):
        BaseService.initCommandChannels(self)


    def traverseDownMessage(self,device_id,message):
        """发送设备消息"""
        # adapter = self.adapters.get(device_id)
        broker = instance.messageBrokerManager.get('redis')
        name = DeviceChannelPubTraverseDown.format(device_id=device_id)
        broker.conn.publish(name,message.marshall(''))




"""
Redis
设备最新的位置、报警、心跳时间

Mongodb
各种运行、配置、日志信息 

Redis-Queue/Publish
消息推送、 设备在线命令推送

"""