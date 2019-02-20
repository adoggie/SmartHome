#coding:utf-8

import os,os.path
import base64
import concox_ev25 as concox
from mantis.fundamental.application.app import instance
from mantis.BlueEarth.vendor.concox.gt310.message import *
from mantis.fundamental.utils.timeutils import  timestamp_current,str_to_timestamp,timestamp_to_str
from mantis.BlueEarth import model
from mantis.BlueEarth.types import PositionSource

class DataAdapter(concox.DataAdapter):
    """处理设备上传消息的应用层逻辑"""
    def __init__(self):
        concox.DataAdapter.__init__(self)

        self.audio_total_size = 0
        self.audio_data = ''
        self.audio_temp_path = self.service.getConfig().get('audio_path')

    def handle(self,message):
        """
        接收到设备标识信息时，需要设置 socket conn的标识属性
        if message isinstance MessageLogin:
            self.conn.client_id.unique_id = message.imei
        """
        concox.DataAdapter.handle(self,message)

        if isinstance(message,(MessageWifiExtension,)):
            self.handle_location(message)
        elif isinstance(message,MessageAudioData):
            self.handle_audio_record(message)


    def handle_audio_record(self,message):
        """这里处理录音记录，需要将接收到的消息通过redis分派出去处理，
        防止程序阻塞(ffmpeg)
        """
        if message.offset == 0:
            self.audio_total_size = message.total_size
            self.audio_data = ''

        self.audio_data = self.audio_data + message.content
        if len(self.audio_data) == self.audio_total_size:
            audio = model.AudioRecord()
            audio.device_id = self.device_id
            audio.device_type = self.device_type
            audio.ymdhms = message.ymdhms
            audio.report_time = timestamp_current()
            audio.size = len(self.audio_data)
            audio.content = base64.b64encode(self.audio_data)
            audio.format = 'amr'
            audio.save()

            timestr = timestamp_to_str(audio.report_time,fmt='%Y%m%d_%H%M%S')
            amr = os.path.join(self.audio_temp_path, '{}_{}_{}.amr'.format(self.device_type,self.device_id,timestr))
            mp3 = os.path.join(self.audio_temp_path, '{}_{}_{}.mp3'.format(self.device_type,self.device_id,timestr))
            f = open( amr, 'wb')
            f.write(self.audio_data)
            f.close()
            os.system('ffmpeg -i {} {}'.format(amr,mp3))

            f = open(mp3,'rb')
            data = f.read()
            f.close()
            audio.content = base64.b64encode(data)
            audio.format = 'mp3'
            audio.save()

            self.audio_data = ''


    def handle_location_wifi(self,message,pos):
        """尚未对wifi进行定位处理，暂时同lbs处理一致"""
        if isinstance(message, MessageWifiExtension):
            pos.position_source = PositionSource.WIFI
            pos.timestamp = str_to_timestamp(message.ymdhms)
            self.convertWifiLocation(pos,message)
            if pos.lat == 0:
                self.convertLbsLocation(pos)

    def convertWifiLocation(self,pos,message):
        """lbs: MessageLbsStationExtension
            查询pos
            lbs_cell 表务必要建索引:
            use constant_reference
            db.lbs_cell.createIndex({'mcc':1,'mnc':1,'lac':1,'cell':1});
        """
        from mantis.BlueEarth.tools.lbs import gd_convert_wifi_location
        import traceback

        ak = self.service.getConfig().get('lbs_ak')
        imei = self.device_id
        # bts = (pos.mcc,pos.mnc,pos.lac,pos.cell_id,pos.signal)
        macs = map(lambda wifi: (wifi['mac'],wifi['signal']),message.wifi_data)
        try:
            data = gd_convert_wifi_location(ak,imei,macs,debug=instance.getLogger().debug)
            object_assign(pos,data)

            # pos.position_source = PositionSource.LBS
        except:
            traceback.print_exc()
            self.logger.error('wifi query fail.' )