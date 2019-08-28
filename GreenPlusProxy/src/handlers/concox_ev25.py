#coding:utf-8

import concox
from mantis.BlueEarth.vendor.concox.ev25.message import *
from mantis.fundamental.utils.timeutils import  timestamp_current,str_to_timestamp
from mantis.BlueEarth import model
from mantis.BlueEarth.types import PositionSource

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
        if isinstance(message, MessageOnlineCommand):
            self.handle_online_command_report(message)


    def handle_location_gps(self,message,pos):
        if isinstance(message, MessageGpsLocation):
            pos.position_source = PositionSource.GPS
            pos.timestamp = str_to_timestamp(message.location.ymdhms)
            if pos.lat == 0:  # 如果gps位置无效，则通过lbs定位
                # print 'Invalid Lat/Lon.', pos.lat,pos.lon
                self.logger.info('{} {} Gps Location Invalid, Try to LBS Calc..'.format(self.device_id,self.device_type))
                self.logger.info(str(message.dict()))
                self.convertLbsLocation(pos)

    def handle_location_lbs(self,message,pos):
        if isinstance(message,MessageLbsStationExtension):
            pos.position_source = PositionSource.LBS
            pos.timestamp = str_to_timestamp(message.ymdhms)
            self.convertLbsLocation(pos)