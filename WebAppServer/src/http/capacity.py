#coding:utf-8
"""
定义产品功能特性
"""

from mantis.fundamental.utils.useful import hash_object

class DeviceCapacity(object):
    def __init__(self):
        self.dial = True        # 支持语音通话
        self.listen = True      # 远程监听
        self.recording = True   # 远程录音
        self.pos_wifi = True    # 支持wifi定位
        self.pos_gps = True     #  gps 定位
        self.pos_lbs = True     # 支持lbs定位


class DeviceGt310(DeviceCapacity):
    def __init__(self):
        DeviceCapacity.__init__(self)

class DeviceGt03(DeviceCapacity):
    def __init__(self):
        DeviceCapacity.__init__(self)
        self.dial = False
        self.recording = False
        self.pos_wifi = False

class DeviceEv25(DeviceCapacity):
    def __init__(self):
        DeviceCapacity.__init__(self)
        self.dial = False
        self.recording = False
        self.listen = False
        self.pos_wifi = False


device_tables={
    'ev25': DeviceEv25,
    'gt310': DeviceGt310,
    'gt03': DeviceGt03
}

def get_product_features(device_type):
    data = {}
    devicecls = device_tables.get(device_type)
    if devicecls:
        data = devicecls().__dict__
    return data

if __name__ == '__main__':
    print get_product_features('ev25')