#coding:utf-8

import concox
from mantis.BlueEarth.vendor.concox.gt03.message import *

class DataAdapter(concox.DataAdapter):
    """处理设备上传消息的应用层逻辑"""
    def __init__(self):
        concox.DataAdapter.__init__(self)

    def handle(self,message):
        """
        接收到设备标识信息时，需要设置 socket conn的标识属性
        if message isinstance MessageLogin:
            self.conn.client_id.unique_id = message.imei
        """
        concox.DataAdapter.handle(self,message)
        # 处理位置信息
        if isinstance(message,(MessageGpsLocation,MessageLbsStationExtension)):
            self.handle_location(message)
        elif isinstance(message,MessageAlarmData):
            self.handle_gps_alarm(message)
        elif isinstance(message,MessageLbsAlarmData):
            self.handle_lbs_alarm(message)

