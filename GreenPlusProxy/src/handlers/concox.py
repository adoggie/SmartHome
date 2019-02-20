#coding:utf-8

import json
import time, os,os.path
import gevent
from gevent.queue import Queue
from mantis.fundamental.application.app import instance
from mantis.BlueEarth.vendor.concox.gt03.message import *
from mantis.BlueEarth.vendor.concox.gt03.packet import NetWorkPacket
from mantis.BlueEarth.constants import *
from mantis.fundamental.utils.timeutils import timestamp_current,current_datetime_string
from mantis.BlueEarth import model
from mantis.BlueEarth.utils import RedisIdGenerator
from mantis.fundamental.utils.importutils import import_class
from mantis.BlueEarth.vendor.concox.gt03.message import MessageOnlineCommand
from mantis.BlueEarth.types import PositionSource,AlarmSourceType,CoordinateType
from mantis.fundamental.utils.timeutils import str_to_timestamp,timestamp_current

class DataAdapter(object):
    """处理设备上传消息的应用层逻辑"""
    def __init__(self):
        self.cfgs = None
        self.conn = None
        self.session = None
        self.service = instance.serviceManager.get('main')
        self.mongo = instance.datasourceManager.get('mongodb').conn
        self.redis = instance.datasourceManager.get('redis').conn
        self.accumulator = None
        self.raw_file = None
        self.active = False  # 设备是否在线登录
        self.start_time = datetime.datetime.now()
        self.device_id = None
        self.redis = None
        self.obj = None
        self.logger = None
        self.seq_gen = None #RedisIdGenerator().init('')
        self.packet_sequence = 0
        self.device_pub_channel = None
        self.device_app_pub_channel = None
        self.command_controller = None
        self.queue = Queue()
        self.running = True
        self.peer_address = ''
        self.last_heartbeat = 0

    def next_packet_sequence(self):
        self.packet_sequence+=1
        if self.packet_sequence >= 0x8000:
            self.packet_sequence = 1
        return self.packet_sequence

    @property
    def device_type(self):
        return self.cfgs.get('device_type')

    def setAccumulator(self,acc):
        self.accumulator = acc

    def handle(self,message):
        """
        接收到设备标识信息时，需要设置 socket conn的标识属性
        if message isinstance MessageLogin:
            self.conn.client_id.unique_id = message.imei
        """
        # self.logger.debug( str( message.__class__ ))
        self.logger.debug('{} conn:{}'.format(str(self),str(self.conn)))
        self.logger.debug(message.__class__.__name__+' device_type:{} device_id:{} message type:0x{:02x} '.format(self.device_type,self.device_id,message.Type.value))
        self.logger.debug(
            message.__class__.__name__ + ' device_type:{} device_id:{} content: {} '.format(self.device_type,
                                                                                                      self.device_id,
                                                                                                      message.dict()))
        if not self.active:
            if isinstance(message, MessageLogin):
                self.device_id = message.device_id
                bytes = message.response()
                self.conn.sendData(bytes)
                self.onActive()
            else:
                self.logger.error('first message is not MessageLogin, destroy socket connection.')
                self.close()
                # return

        message.device_id = self.device_id
        message.device_type = self.device_type

        self.distribute_message(message)

        if isinstance(message,MessageHeartBeat):
            self.last_heartbeat = timestamp_current()
            self.handle_heartbeat(message)
        if isinstance(message,MessageAdjustTime):
            bytes = message.response()
            self.conn.sendData(bytes)
        if isinstance(message, MessageOnlineCommand):
            self.handle_online_command_report(message)

        # 处理位置信息
        # if isinstance(message,(MessageGpsLocation,MessageLbsStationExtension)):
        #     self.handle_location(message)
        # elif isinstance(message,MessageAlarmData):
        #     self.handle_gps_alarm(message)
        # elif isinstance(message,MessageLbsAlarmData):
        #     self.handle_lbs_alarm(message)


    def handle_online_command_report(self,message):
        data = message.parseContent()
        fence_data = {}
        config = {}
        for k,v in data.items():
            cap = 'fence_'
            if k.find(cap)==0:
                name = k.split(cap)[1]
                fence_data[name] = v
            else:
                config[k] = v
        fence = model.Fence.get_or_new(device_id=self.device_id)
        object_assign(fence,fence_data)
        fence.device_id = self.device_id
        fence.device_type = self.device_type

        devcfg = model.DeviceConfig.get_or_new(device_id=self.device_id)
        object_assign(devcfg,config)
        devcfg.device_id = self.device_id
        devcfg.device_type = self.device_type

        fence.save()
        devcfg.save()



    def handle_gps_alarm(self,message):
        """处理gps报警"""
        alarm = model.AlarmData()
        alarm.alarm_source_type = AlarmSourceType.GPS_ALARM

        pos = self.make_position()
        pos.timestamp = str_to_timestamp(message.location.ymdhms)
        object_assign(pos, message.dict())
        if message.location.located =='y':
            # 设备gps已定位
            pos.position_source = PositionSource.GPS
        else: # 从lbs中判别坐标
            pos.position_source = PositionSource.LBS
            self.convertLbsLocation(pos)
        self.savePosition(pos)

        data = hash_object(pos,excludes=('_id',))
        object_assign(alarm,data)

        alarm.alarm_name = AlarmType.get_name(message.location_ext.alarm)
        alarm.save()


    def handle_lbs_alarm(self,message):
        """处理lbs报警"""
        alarm = model.AlarmData()
        alarm.alarm_source_type = AlarmSourceType.LBS_ALARM
        alarm.alarm_name = AlarmType.get_name(message.location_ext.alarm)

        pos = self.make_position()
        pos.timestamp = timestamp_current() # str_to_timestamp(message.location.ymdhms)

        object_assign(pos,message.location_ext.dict())
        pos.position_source = PositionSource.LBS
        self.convertLbsLocation(pos)
        self.savePosition(pos)
        data = hash_object(pos,excludes=('_id',))

        object_assign(alarm,data)

        alarm.alarm_name = AlarmType.get_name(message.location_ext.alarm)
        alarm.save()
        # 推送更新的报警包
        self.device_app_pub_channel.publish_or_produce(json.dumps(data))


    def savePosition(self,pos):
        if pos.lon and pos.lat:
            self.processPosition(pos)
            pos.save()  # insert database
            self.logger.debug('{} {} position content: {}'.format(self.device_type,self.device_id,pos.dict() ))
            # 更新设备最新的状态和位置信息到Redis
            data = hash_object(pos, excludes=('_id',))
            self.update_device_in_cache(data)

            # 推送更新的定位包
            # data['messsage_type'] = 'position'
            self.device_app_pub_channel.publish_or_produce(json.dumps(data))
        else:
            self.logger.error('Position Lon/Lat is Invalid.')
            # self.logger.error(message.dict())


    def handle_heartbeat(self,message):
        bytes = message.response()
        self.conn.sendData(bytes)

        # 更新设备最新的状态和位置信息到Redis
        data = message.dict()
        self.update_device_in_cache(data)

    def make_position(self):
        pos = model.Position()
        name = DevicePositionLastest.format(device_id=self.device_id)
        data = self.redis.hgetall(name)
        # if data:
        #     object_assign(pos,data)
        pos.device_id = self.device_id
        pos.device_type = self.device_type
        pos.report_time = timestamp_current()

        # 取出当前的信号值、电压值
        if data:
            pos.gsm = data.get('gsm', 0)
            pos.voltage = data.get('voltage', 0)
        return pos

    def handle_location(self,message):
        """处理Gps/Lbs定位信息
        """
        pos = self.make_position()

        data = message.dict()
        object_assign(pos, data)

        self.handle_location_gps(message,pos)
        self.handle_location_lbs(message,pos)
        self.handle_location_wifi(message,pos)

        # 有效的经纬度坐标才进行保存， lbs 上行的数据存在无法匹配的情况
        self.savePosition(pos)

    def handle_location_gps(self,message,pos):
        if isinstance(message, MessageGpsLocation):
            pos.position_source = PositionSource.GPS
            pos.timestamp = str_to_timestamp(message.location.ymdhms)

    def handle_location_lbs(self,message,pos):
        if isinstance(message,MessageLbsStationExtension):
            pos.position_source = PositionSource.LBS
            pos.timestamp = str_to_timestamp(message.ymdhms)
            self.convertLbsLocation(pos)

    def handle_location_wifi(self,message,pos):
        pass

    def update_device_in_cache(self,data):
        data['update_time'] = timestamp_current()
        key = DevicePositionLastest.format(device_id=self.device_id)
        self.redis.hmset(key, data)

    def _convertLbsLocation(self,pos):
        """lbs: MessageLbsStationExtension
            查询pos
            lbs_cell 表务必要建索引:

            use constant_reference
            db.lbs_cell.createIndex({'mcc':1,'mnc':1,'lac':1,'cell':1});
        """
        name = self.service.getConfig().get('table_name_lbs_cell')
        coll = self.mongo['constant_reference'][name]
        querycase ={
            'mcc':pos.mcc,
            'mnc':pos.mnc,
            'lac':pos.lac,
            'cell':pos.cell_id
        }
        obj = coll.find_one(querycase)
        if obj:
            lon = obj['lon']
            lat = obj['lat']
            addr = obj['addr']
            pos.lon = lon
            pos.lat = lat
            pos.address = addr
        else:
            self.logger.error('lbs query fail.' + str(querycase))

    def convertLbsLocation(self,pos):
        """lbs: MessageLbsStationExtension
            查询pos
            lbs_cell 表务必要建索引:
            use constant_reference
            db.lbs_cell.createIndex({'mcc':1,'mnc':1,'lac':1,'cell':1});
        """
        from mantis.BlueEarth.tools.lbs import gd_convert_lbs_location

        ak = self.service.getConfig().get('lbs_ak')
        imei = self.device_id
        # bts = (pos.mcc,pos.mnc,pos.lac,pos.cell_id,pos.signal)
        bts = self.makeLbsBts(pos)
        bts = bts[:1]
        try:
            data = gd_convert_lbs_location(ak,imei,bts,debug=instance.getLogger().debug)
            object_assign(pos,data)
            pos.position_source = PositionSource.LBS
        except:
            self.logger.error('lbs query fail.' )

    def convertSignalValue(self,value):
        # (如获得信号强度为正数，则请按照以下公式进行转 换:获得的正信号强度 * 2 – 113)
        # return value
        if value > 0:
            value  = value*2 - 133
        return value

    def makeLbsBts(self,pos):
        result = []
        message = pos
        mcc = message.mcc
        mnc = message.mnc



        rssi = self.convertSignalValue(message.rssi)
        bts = [mcc,mnc,message.lac,message.cell_id,rssi]
        result.append(bts)

        main = bts

        if message.lac1:
            rssi = self.convertSignalValue(message.rssi1)
            bts = [mcc, mnc, message.lac1, message.ci1, rssi]
            result.append(bts)
            # if rssi > main[4]: main= bts

        if message.lac2:
            rssi = self.convertSignalValue(message.rssi2)
            bts = [mcc, mnc, message.lac2, message.ci2, rssi]
            result.append(bts)
            # if rssi > main[4]: main = bts

        if message.lac3:
            rssi = self.convertSignalValue(message.rssi3)
            bts = [mcc, mnc, message.lac3, message.ci3, rssi]
            result.append(bts)
            # if rssi > main[4]: main = bts

        if message.lac4:
            rssi = self.convertSignalValue(message.rssi4)
            bts = [mcc, mnc, message.lac4, message.ci4, rssi]
            result.append(bts)
            # if rssi > main[4]: main = bts

        if message.lac5:
            rssi = self.convertSignalValue(message.rssi5)
            bts = [mcc, mnc, message.lac5, message.ci5, rssi]
            result.append(bts)
            # if rssi > main[4]: main = bts

        if message.lac6:
            rssi = self.convertSignalValue(message.rssi6)
            bts = [mcc, mnc, message.lac6, message.ci6, rssi]
            result.append(bts)
            # if rssi > main[4]: main = bts
        return result



    def processPosition(self,pos):
        """逆地址转换"""
        from mantis.BlueEarth.tools.coord_transform import wgs84_to_bd09
        from mantis.BlueEarth.tools.geotools import geocoding_address
        lon,lat = wgs84_to_bd09(pos.lon,pos.lat)
        if not pos.address:
            pos.address = geocoding_address(lon,lat)
        # pos.lon_bd = lon
        # pos.lat_bd = lat

    def distribute_message(self,message):
        data = message.dict()

        data['name'] = message.__class__.__name__
        data['type_id'] = message.Type.value
        data['type_comment'] = message.Type.comment
        data['timestamp'] = timestamp_current()
        data['datetime'] = current_datetime_string()
        data['device_id'] = self.device_id
        data['device_type'] = self.device_type

        if data.has_key('extra'): del data['extra']
        if data.has_key('Type'): del data['Type']

        print data
        #将设备消息发布出去
        self.service.dataFanout('switch0',json.dumps(data))

        # 发布到隶属于设备编号的通道上去
        self.device_pub_channel.publish_or_produce(json.dumps(data))

        # # 写入日志数据库
        dbname = 'blue_earth_device_log'
        coll = self.mongo[dbname][self.device_id]
        coll.insert_one(data)

    def init(self,cfgs):
        self.cfgs = cfgs
        self.redis = instance.datasourceManager.get('redis').conn
        self.logger = instance.getLogger()
        self.seq_gen = RedisIdGenerator().init(self.cfgs.get('sequence_key'))

        cls = import_class(self.cfgs.get('command_controller'))
        self.command_controller = cls()
        gevent.spawn(self.messageTask)
        return self

    def open(self):
        pass

    def setConnection(self,sock_conn):
        self.conn = sock_conn

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()

    def onConnected(self,sock_con,address,*args):
        """连接上来"""
        self.logger.debug('device connected .  {}'.format(str(address)))
        self.setConnection(sock_con)
        self.peer_address = address # 连接上来的对方地址
        self.last_heartbeat = timestamp_current()

        # self.make_rawfile()

    def make_rawfile(self):
        fmt = '%Y%m%d_%H%M%S.%f'
        ts = time.time()
        name = time.strftime(fmt, time.localtime(ts)) + '.raw'
        name = os.path.join(instance.getDataPath(),name)
        self.raw_file = open(name,'w')

    def onDisconnected(self):
        self.logger.debug('device  disconnected. {} {}'.format(self.device_type,self.device_id))
        self.active = False
        # self.raw_file.close()
        self.service.deviceOffline(self)
        self.running = False

        # 断开连接删除设备与接入服务器的映射
        self.redis.delete(DeviceLandingServerKey.format(self.device_id))

    def hex_dump(self,bytes):
        dump = ' '.join(map(lambda _:'%02x'%_, map(ord, bytes)))
        return dump

    def dump_hex_data(self,data):
        fmt = '%Y%m%d_%H%M%S'
        ts = time.time()
        times = time.strftime(fmt, time.localtime(ts))

        name = 'data_{}.hex'.format(self.device_type)
        name = os.path.join(instance.getDataPath(), name)

        fp = open(name, 'a+')
        fp.write(times +','+ data + '\n')
        fp.close()

    def onData(self,bytes):
        """ raw data """
        self.logger.debug("device data retrieve in . {} {}".format(self.device_id,self.device_type))
        dump = self.hex_dump(bytes)
        self.logger.debug("<< "+dump)

        self.dump_hex_data(dump)
        # self.raw_file.write(bytes)
        # self.raw_file.flush()
        messages = self.accumulator.enqueue(bytes)
        for message in messages:
            # self.handle(message)
            self.queue.put([message,current_datetime_string()])

    def onActive(self):
        """设备在线登录了"""
        self.logger.debug('device onActive. {} {}'.format(self.device_type, self.device_id))

        self.active = True
        # 启动命令发送任务，读取下发命令
        gevent.spawn(self.commandTask)


        access_url = self.service.getConfig().get('access_command_url')
        self.redis.set(DeviceLandingServerKey.format(self.device_id),access_url)


        self.redis.hset(DeviceActiveListKeyHash,self.device_id,timestamp_current())
        obj = model.Device.get(device_id = self.device_id)
        if obj:
            self.obj = obj
        else:
            self.logger.debug('device: {} not found in database.'.format(self.device_id))
            # self.obj = model.Device()
            # self.obj.device_id = self.device_id
            # self.obj.name = self.device_id
            # self.obj.device_type = self.device_type
            # self.obj.save()

        self.service.deviceOnline(self)

        # 创建通道
        address = DeviceChannelPub.format(device_id=self.device_id)
        broker = instance.messageBrokerManager.get('redis')
        self.device_pub_channel = broker.createPubsubChannel(address)
        self.device_pub_channel.open()

        # 创建应用通道
        address = DeviceAppChannelPub.format(device_id=self.device_id)
        broker = instance.messageBrokerManager.get('redis')
        self.device_app_pub_channel = broker.createPubsubChannel(address)
        self.device_app_pub_channel.open()

        # 查询一次设备运行配置信息
        # self.queryDeviceConfig()

    def queryDeviceConfig(self):
        """一次查询设备所有运行配置参数"""
        from mantis.BlueEarth.utils import sendCommand
        cmds = self.command_controller.init_commands()
        for cmd in cmds:
            sendCommand(self.device_id,self.device_type,cmd)

    def commandTask(self):
        """从redis中读取设备的命令，并进行发送到设备"""
        key = DeviceCommandQueue.format(device_type = self.device_type,device_id = self.device_id)
        while self.active:
            data = self.redis.blpop(key,1)
            if data:
                key,content = data
                if not content:
                    continue

                if not self.sendCommand(content):
                    break

                # content = self.command_controller.execute(content)
                # if not content:
                #     continue
                #
                # self.logger.debug('SendCommand: {} {} {}'.format(content,self.device_id,self.device_type))
                # command = MessageOnlineCommand()
                # command.content = content
                # command.sequence = self.seq_gen.next_id()
                # packet = command.packet()
                # packet.sequence = self.next_packet_sequence()
                # self.conn.sendData(packet.to_bytes())
                #
                # # save send record
                # send = model.CommandSend()
                # send.device_id = self.device_id
                # send.send_time = timestamp_current()
                # send.sequence = packet.sequence
                # send.command = command.content
                # send.save()
        self.logger.debug('commandTask Exiting.. {} {}'.format(self.device_type, self.device_id))

    def sendCommand(self,command):

        content = command
        content = self.command_controller.execute(content)
        if not content:
            return True

        self.logger.debug('SendCommand: {} {} {}'.format(content,self.device_id,self.device_type))
        command = MessageOnlineCommand()
        command.content = content
        command.sequence = self.seq_gen.next_id()
        packet = command.packet()
        packet.sequence = self.next_packet_sequence()
        try:
            self.conn.sendData(packet.to_bytes())
        except:
            self.logger.error('socket sendData error. {} {} {}'.format(content,self.device_id,self.device_type))
            self.close()
            return False
        # save send record
        send = model.CommandSend()
        send.device_id = self.device_id
        send.send_time = timestamp_current()
        send.sequence = packet.sequence
        send.command = command.content
        send.save()
        return True
        # self.logger.debug('commandTask Exiting.. {} {}'.format(self.device_type, self.device_id))


    def messageTask(self):
        import traceback

        while self.running:
            # 长久没有心跳包
            if timestamp_current() - self.last_heartbeat > MaxLiveTimeDeviceLandingServerKey:
                self.logger.warn('device heartbeat timer reached limit. close socket. {} {} '.format(self.device_id, self.device_type))
                self.close()
                break
            try:
                message,date = self.queue.get(block=True, timeout=1)
                try:
                    self.logger.debug('message pop from queue: {} {}  {} {}'.format(date,message.__class__.__name__,self.device_id,self.device_type))
                    self.handle(message)
                except:
                    self.logger.warn(traceback.print_exc())
            except:pass

        self.logger.warn('messageTask() exiting.. {} {} '.format(self.device_id, self.device_type))




