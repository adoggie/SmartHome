#coding:utf-8

from mantis.fundamental.utils.useful import hash_object,object_assign
from bson import ObjectId

database = None



class Model(object):
    def __init__(self):
        self._id = None
        self.__collection__ = self.__class__.__name__

    # @staticmethod
    # def find(self,**kwargs):
    #     pass
    #
    # @staticmethod
    # def get(self,**kwargs):
    #     pass

    @classmethod
    def get(cls,id):
        obj = cls()
        coll =  database[obj.__collection__]
        data = coll.find_one({'_id':ObjectId(id)})
        if data:
            object_assign(obj,data)
            return obj
        return None

    def delete(self):
        """删除当前对象"""
        coll = database[self.__collection__]
        coll.delete_one({'_id':self._id})

    def update(self,**kwargs):
        """执行部分更新"""
        coll = database[self.__collection__]
        coll.update_one({'_id':self._id},update={'$set':kwargs},upsert = True)
        return self

    def save(self):
        coll = database[self.__collection__]
        data = hash_object(self, excludes=['_id'])
        if self._id:
            self.update(**data)
        else:
            self._id = coll.insert_one(data)
        return self

    @classmethod
    def spawn(cls,data):
        """根据mongo查询的数据集合返回类实例"""

        # 单个对象
        if isinstance(data,dict):
            obj = cls()
            object_assign(obj,data)
            return obj
        # 集合
        rs = []
        for r in data:
            obj = cls()
            object_assign(obj, data)
            rs.append(obj)
        return rs

    @classmethod
    def create(cls,**kwargs):
        obj = cls()
        object_assign(obj,kwargs)
        return obj


class Device(Model):
    """设备信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''     # 设备唯一编号
        self.device_type = ''   # 设备类型 gt310,..
        self.name = ''          # 设备名称
        self.imei = ''          # 硬件编码
        self.sim = ''           # sim卡号
        self.mobile = ''        # 移动电话
        self.password = ''      # 设备管理密码
        self.admin_mobile = ''  # 管理手机号，用于密码找回
        self.active = False     # 是否激活启用
        self.active_time = 0    # 开通时间
        self.expire_time = 0    # 过期时间
        self.update_time = 0    # 更新时间


class User(Model):
    def __init__(self):
        Model.__init__(self)
        self.account = ''       # 账户名
        self.password = ''      # 登录密码
        self.salt = ''          # 随机数
        self.user_type = ''     # admin,user
        self.name   = ''        # 用户名称
        self.wx_user  = ''      # 微信账号
        self.avatar   = ''      # 头像
        self.mobile     = ''    # 移动电话
        self.last_login = 0     # 登录时间
        self.expire_time = 0    # 过期时间
        self.update_time = 0    # 更新时间


class Group(Model):
    """设备组，可进行分级，父子管理"""
    def __init__(self):
        Model.__init__(self)
        self.name = ''          #
        self.order = 0
        self.parent = 0
        self.path = ''
        self.user_id = ''       # 隶属于用户


class DeviceGroupRelation(Model):
    """组合设备关系 , N对N关系"""
    def __init__(self):
        Model.__init__(self)
        self.group_id = ''   # 组编号
        self.device_id = ''  # 设备编号
        self.update_time = 0    # 更新时间

class DeviceUserRelation(Model):
    """设备与用户关系 ( N - N )"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''       # 用户编号
        self.device_id = ''     # 设备记录编号
        self.device_name = ''   # 设备名称

        self.update_time = 0    # 更新时间
        self.is_share_device = False  # 是否是分享设备
        self.share_user_id = ''     # 分享设备的用户编号 冗余
        self.share_device_link  = ''   # 如果是他人分享

class SharedDeviceLink(Model):
    """用户分享的设备"""
    def __init__(self):
        Model.__init__(self)
        self.user_id = ''       # 分享用户编号
        self.device_id = ''     # 分享的设备
        self.name = ''          # 分享的名称
        self.expire_time = 0    # 分享到期时间
        self.password = ''      # 访问密码（可以为空不设置)


class ShareDeviceToTarget(Model):
    """将设备分享给多个用户"""
    def __init__(self):
        Model.__init__(self)
        self.share_device_id = ''   # SharedDevice
        self.target_user = ''       # 分享的目标用户，微信用户
        self.wx_link = ''           # 微信分享链接
        self.code_2d = ''           # 二维码
        self.message = ''           # 留言


class  Position(Model):
    """设备位置信息"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''         # 设备编号
        self.lon = 0                # 经度
        self.lat = 0                # 维度
        self.heading = 0            # 方向
        self.speed = 0              # 速度
        self.altitude = 0           # 海拔

        self.ymdhms = ''            #
        self.mcc = 0
        self.mnc = 0
        self.lac = 0
        self.cell_id = 0
        self.satellite = 0
        self.acc = 0
        self.report_mode = 0        # 上报模式
        self.up_mode = 0            # 上报实时、追加
        self.miles = 0              # 里程数
        # 2.
        self.oil_bit7 = 0           # 1:油电断开
        self.gps_bit6 = 0           # GPS 是否已定位
        self.charging_bit2 = 0      # 已接电源充电
        self.acc_bit1 = 1           # 1:ACC 高 , 0:ACC 低
        self.fortify_bit0 = 1       # 1:设防 , 0:撤防

        # 3.
        self.voltage = 0            # 电压
        self.gsm = 0                # 信号

        self.report_time = 0  # 报告时间

class AlarmData(Model):
    """设备报警信息"""
    def __init__(self):
        Model.__init__(self)
        self.type = 0       # 报警类型
        self.pos_id = None     # 位置记录 Position


class CommandSend(Model):
    """设备在线命令发送记录"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''         # 设备编号
        self.send_time = 0          # 发送时间
        self.sequence = 1           # 系统流水号
        self.ack_time = 0           # 回应时间
        self.command = ''           # 命令名称
        self.content = ''           # 命令参数

class  DeviceConfig(Model):
    """设备运行配置参数"""
    def __init__(self):
        Model.__init__(self)
        self.device_id = ''         # 设备编号
        self.device_type = ''       # gt310
        self.ASETAPN = ''           # APN自适应
        self.ASETGMT = ''           # 时区自适应
        self.SERVER = ''            # 后台服务器参数设置
        self.GMT = ''               # 时区设置
        self.LANG = ''              # 语言设置
        self.SOS = ''               # SOS号码设置
        self.HBT = ''               # 心跳包设置间隔
        self.ANGLEREP = ''          # 拐点补传设置
        self.SENSOR = ''            # 震动检测时间
        self.SENDS = ''            # SENSOR 控制 GPS 时间
        self.GFENCE = ''            # 设置围栏报警
        self.BATALM = ''            # 低电报警
        self.SOSALM = ''            # SOS 报警
        self.CALL = ''            # 电话重拨次数
        self.LEVEL = ''            # SENSOR灵敏度设置
        self.SENSORSET = ''        # 设置触发震动激活GPS工作条件
        self.ALMREP = ''        # 设置接收报警号码（除SOS报警）
        self.MODE = ''        # 模式设置（模式1、2）
        self.ICCID = ''        # ICCID号点名查询
        self.IMSI = ''        # IMSI
        self.FIXMODE = ''        # 定位方式开关
        self.FIXPRI = ''        # 定位方式优先级设置
        self.FLY = ''        # 飞行状态开关








from mantis.fundamental.nosql.mongo import Connection
if __name__ == '__main__':
    conn = Connection().conn
    coll = conn['TradeLog_Ctp_htqh-01']['send_order']
    rs = coll.find()
    for r in rs :
        print r
    # print type(rs)