#coding:utf-8

import json
from flask import Flask,request
from flask import Response

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.webapi import *
from mantis.fundamental.flask.utils import nocache
from mantis.fanbei.smarthome import model
from mantis.fanbei.smarthome.message import *
from mantis.fanbei.smarthome.errors import *

def get_active_devices():
    """获取在线设备"""
    cr  =CR()
    main = instance.serviceManager.get('main')
    adapters = main.getActivedDevices()
    result=[]
    for adapter in adapters:
        device_id = adapter.device_id
        device_type = adapter.device_type
        device = model.SmartDevice.get(device_id=device_id)
        if device:
            item ={'device_id':device_id,'name':device.name,'device_type':device_type}
            result.append(item)
    cr.assign(result)
    return cr.response

def get_device_profile():
    """获取设备的安装profile信息"""
    device_id = request.values.get('id')
    device = model.SmartDevice.get(id = device_id)
    if not device_id:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    result = ''
    if device.profile:
        result = json.loads(device.profile)
    return CR(result=result).response

def send_command():
    """获取在线设备,可控制是否设备离线发送还是在线发送"""
    main = instance.serviceManager.get('main')
    cr  =CR()
    print request.query_string
    device_id = request.values.get('id')
    device_command = request.values.get('command')
    online = request.values.get('online','false')
    if not device_id or not device_command:
        print 'device_id or command is null.'
        return cr.response
    online_send = False
    if online.lower() == 'true':
        online_send = True
    main.sendCommand(device_id,device_command,online_send)
    return cr.response


def get_device_status():
    """获取指定设备的最新状态(所有sensor的当前最新状态) """
    device_id = request.values.get('id')
    # sensor_type = request.values.get('sensor_type')
    # sensor_id = request.values.get('sensor_id')
    # param_name = request.values.get('param_name')

    rs = model.LogSensorStatus.find(device_id = device_id)
    result = dict(device_id = device_id )

    device = model.LogDeviceStatus.get(device_id = device_id)
    if device:
        result.update( device.dict())

    sensors = []
    for r in rs:
        data = r.dict()
        sensors.append( data )
    result['sensors'] = sensors
    return CR(result=result).response


def query_device_status():
    """发送对设备的状态查询 MessageDeviceStatusQuery
        对device_id的多个sensor发送多个查询 SensorStatusQuery
        对Mcu设备查询 McuStatusQuery
    """
    device_id = request.values.get('id')
    main = instance.serviceManager.get('main')
    main.traverseDownMessage(device_id,MessageDeviceStatusQuery())
    return CR().response


def set_device_value():
    """ 设置指定设备的参数值（等同于控制)
       允许一次发送多个控制命令

       设置当前模式，保存当前模式 ，都以 MessageDeviceValueSet 消息下发
       到设备端，将被转换为 McuValueSet ( d,e 字段)

    """
    device_id = request.values.get('id')
    name = request.values.get('name')
    value = request.values.get('value')
    module = request.values.get('module',1) # 0 : arm , 1:mcu

    message = MessageDeviceValueSet()
    message.device_id = device_id
    message.param_name = name
    message.param_value = value
    message.mod_type = module

    main = instance.serviceManager.get('main')
    main.traverseDownMessage(device_id,message)
    return CR().response


def set_sensor_value():
    """设置指定 端点设备的参数"""
    device_id = request.values.get('id')
    sensor_id = request.values.get('sensor_id')
    sensor_type = request.values.get('sensor_type')
    name = request.values.get('name')
    value = request.values.get('value')

    message = MessageSensorValueSet()
    message.device_id = device_id
    message.sensor_type = sensor_type
    message.sensor_id = sensor_id
    message.param_name = name
    message.param_value = value

    main = instance.serviceManager.get('main')
    main.traverseDownMessage(device_id, message)
    return CR().response


def get_sensor_status():
    """查询指定sensor设备的状态"""
    device_id = request.values.get('id')
    sensor_id = request.values.get('sensor_id')
    sensor_type = request.values.get('sensor_type')
    main = instance.serviceManager.get('main')
    sensor = model.LogSensorStatus.get(device_id=device_id,sensor_id=sensor_id,sensor_type=sensor_type)

    result=dict(sensor_type=sensor_type,sensor_id=sensor_id)
    if sensor:
        result.update( sensor.dict())
    return CR(result=result).response