#coding:utf-8

"""
iot_make_device.py
读取系统数据库中的 设备的profile 记录，生成每一个设备的工作目录以及设备的gateway文件

"""

import shutil
import os.path,os
import json
from collections import OrderedDict

from mantis.fundamental.nosql.mongo import Connection
from mantis.fanbei.smarthome import model
from mantis.fundamental.parser.yamlparser import YamlConfigParser
from mantis.fundamental.utils.timeutils import timestamp_current
from mantis.fundamental.utils.useful import object_assign

def get_database():
    db = Connection('SmartHome').db
    return db
model.set_database(get_database())

# =================================================
DATA_ROOT='./data'
PlatformPort = 8943
PlatformAddr = '117.78.47.187'

table_device_type = {
    2 : "light"
}
# =================================================


def get_device_profile_data(device_id):
    device = model.SmartDevice.get(id = device_id)
    template = model.RoomTemplate.get( id = device.template_id )
    data = template.profile
    return json.loads(data)



def get_sensor_list(device_id):
    """转换profile为 rokid识别的格式"""

    result = []
    defines={}

    profile = get_device_profile_data(device_id)
    for item in profile["sensor_defines"]:
        defines[item["type"]] = item

    for sensor  in profile.get("sensors"):
        type_ = sensor['type']
        id_ = sensor['id']
        uid = "{}-{}-{}".format(device_id,type_, id_)
        type_info = defines[type_]

        device = dict(
                       Name = type_info['name'],
                       NodeId = uid,
                       ManufacturerName = type_info['vendor'],
                       ManufacturerId = type_info['vendor'],
                       DeviceType = table_device_type[type_],
                       Model = type_info['model'],
                       ProtocolType = 'z-wave'
                       )

        result.append(device)
    return result


def init_device(datapath, device):
    path = os.path.join(DATA_ROOT,device.id)
    if not os.path.exists(path):
        os.makedirs(path)

    values = OrderedDict( mac = device.id , platformPort = PlatformPort,
                   platformAddr = PlatformAddr , manufacturerId = device.vendor ,
                   deviceType='sb01',
                   model = 'sb-2019',
                   protocolType = 'z-wave')


    # 读取profile 生成多个sensor
    # values['sensor_num ']
    sensors = get_sensor_list(device.id)
    values['sensor_num'] = len(sensors)
    for i,s in enumerate(sensors):
        values['sensor_{}.Name'.format(i+1)] = s['Name']
        values['sensor_{}.NodeId'.format(i+1)] = s['NodeId']
        values['sensor_{}.ManufacturerName'.format(i+1)] = s['ManufacturerName']
        values['sensor_{}.ManufacturerId'.format(i+1)] = s['ManufacturerId']
        values['sensor_{}.DeviceType'.format(i+1)] = s['DeviceType']
        values['sensor_{}.Model'.format(i+1)] = s['Model']
        values['sensor_{}.ProtocolType'.format(i+1)] = s['ProtocolType']

    filename = os.path.join(path,'gateway.txt')
    fp = open(filename,'w')

    for name,value  in values.items():
        fp.write( name + ' = '+ unicode(value).encode('utf-8') + '\n')
    fp.close()

def init_all():
    if not os.path.exists(DATA_ROOT):
        os.makedirs(DATA_ROOT)
    devices = model.SmartDevice.find()
    for device in devices:
        init_device(DATA_ROOT,device)


if __name__ == '__main__':
    init_all()