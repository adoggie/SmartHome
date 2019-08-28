#coding:utf-8

import json
from flask import Flask,request,g
from flask import Response
import time
from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.webapi import *
from mantis.fundamental.utils.useful import make_salt
from mantis.fundamental.flask.utils import nocache
from mantis.fanbei.smarthome import model
from mantis.fanbei.smarthome.message import *

from mantis.fanbei.smarthome import constants
from mantis.fanbei.smarthome.errors import ErrorDefs

from functools import wraps, update_wrapper

def check_authcode(view):
    """检验请求 authcode
        authcode : { app_id, create_time }
    """


    @wraps(view)
    def _wrapper(*args, **kwargs):
        from mantis.fanbei.smarthome.errors import ErrorDefs

        token = request.values.get('authcode','')
        name = constants.AppRequestAuthCodePrefix + token
        redis = instance.datasourceManager.get('redis')
        data = redis.conn.get(name)
        if not data:
            return ErrorReturn(ErrorDefs.TokenInvalid).response
        authdict = json.loads(data)

        if not authdict:
            return ErrorReturn(ErrorDefs.TokenInvalid).response

        create_time = authdict.get('create_time',0)
        if time.time() - create_time > 3600 * 24 * 200:
            return ErrorReturn(ErrorDefs.ResExpired).response   # 申请的authcode过期

        g.auth = authdict

        return view(*args,**kwargs)

    # return update_wrapper(_wrapper, view)
    return _wrapper

def getAuthDeviceIds(authcode):
    """从redis读取授权的设备编码, 多个设备编码以 , 分隔"""
    name = constants.AppRequestAuthCodeWidthIdsPrefix + authcode
    redis = instance.datasourceManager.get('redis')
    value = redis.conn.get(name)
    ids = str(value).split(',')
    return ids

@check_authcode
def get_active_devices():
    """获取在线设备"""
    authcode = request.values.get('authcode','')

    cr  =CR()
    main = instance.serviceManager.get('main')
    
    result=[]
    device_ids = getAuthDeviceIds(authcode)

    for device_id in device_ids:
        item = {'id': device_id, 'name': device_id}
        result.append(item)

        # device = model.SmartDevice.get(device_id=device_id)
        # if device:
        #     item ={'id':device_id,'name':device.name,'device_type':device.type}
        #     result.append(item)
    cr.assign(result)
    return cr.response

@check_authcode
def get_device_profile():
    """获取设备的安装profile信息"""
    device_id = request.values.get('id')
    device = model.SmartDevice.get(id = device_id)
    if not device_id:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    result = ''
    profile = device.profile
    if not profile:
        template = model.RoomTemplate.get(id=device.template_id)
        if template:
            profile = template.profile
    if profile:
        result = json.loads(profile)
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

@check_authcode
def get_device_status():
    """获取指定设备的最新状态(所有sensor的当前最新状态) """
    authcode = request.values.get('authcode','')
    device_ids = getAuthDeviceIds(authcode)

    device_id = request.values.get('id')

    if device_id not in device_ids:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    # sensor_type = request.values.get('sensor_type')
    # sensor_id = request.values.get('sensor_id')
    # param_name = request.values.get('param_name')

    rs = model.Sensor.find(device_id = device_id)
    result = dict(device_id = device_id )

    device = model.SmartDevice.get(id = device_id)
    if not device:
        device = model.SmartDevice()
    result.update( device.dict())

    if result.has_key('secret_key'):
        del result['secret_key']

    if result.has_key('profile'):
        del result['profile']

    sensors = []
    for r in rs:
        data = dict(sensor_id=r.id,sensor_type=r.type)
        try:
            params = json.loads(r.params)
            data.update(params)
        except:pass

        sensors.append( data )
    result['sensors'] = sensors
    return CR(result=result).response

@check_authcode
def query_device_status():
    """发送对设备的状态查询 MessageDeviceStatusQuery
        对device_id的多个sensor发送多个查询 SensorStatusQuery
        对Mcu设备查询 McuStatusQuery

        post /smartbox/status/query
    """
    authcode = request.values.get('authcode', '')
    device_ids = getAuthDeviceIds(authcode)

    device_id = request.values.get('id')

    if device_id not in device_ids:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    main = instance.serviceManager.get('main')
    main.traverseDownMessage(device_id,MessageDeviceStatusQuery())
    return CR().response


@check_authcode
def query_sensor_status():
    """发送对设备的状态查询 MessageDeviceStatusQuery
        对device_id的多个sensor发送多个查询 SensorStatusQuery
        对Mcu设备查询 McuStatusQuery

        post /smartbox/sensor/status/query'
    """
    authcode = request.values.get('authcode', '')
    device_ids = getAuthDeviceIds(authcode)

    sensor_id = request.values.get('sensor_id',0,type=int )
    sensor_type = request.values.get('sensor_type',0,type=int )

    device_id = request.values.get('id')

    if device_id not in device_ids:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    main = instance.serviceManager.get('main')
    message = MessageSensorStatusQuery()
    message.sensor_id = sensor_id
    message.sensor_type = sensor_type

    main.traverseDownMessage(device_id,message)
    return CR().response

@check_authcode
def set_device_value():
    """ 设置指定设备的参数值（等同于控制)
       允许一次发送多个控制命令

       设置当前模式，保存当前模式 ，都以 MessageDeviceValueSet 消息下发
       到设备端，将被转换为 McuValueSet ( d,e 字段)

    """
    authcode = request.values.get('authcode', '')
    device_ids = getAuthDeviceIds(authcode)

    device_id = request.values.get('id')
    name = request.values.get('name')
    value = request.values.get('value')
    module = request.values.get('module',1) # 0 : arm , 1:mcu

    if device_id not in device_ids:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    message = MessageDeviceValueSet()
    message.device_id = device_id
    message.param_name = name
    message.param_value = value
    message.mod_type = module

    main = instance.serviceManager.get('main')
    main.traverseDownMessage(device_id,message)
    return CR().response

@check_authcode
def set_sensor_value():
    """设置指定 端点设备的参数
    POST '/smartbox/sensor/params'
    """
    authcode = request.values.get('authcode', '')
    device_ids = getAuthDeviceIds(authcode)

    device_id = request.values.get('id')
    sensor_id = request.values.get('sensor_id',0,type=int)
    sensor_type = request.values.get('sensor_type',0,type=int)
    name = request.values.get('name')
    value = request.values.get('value')

    if device_id not in device_ids:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response


    message = MessageSensorValueSet()
    message.device_id = device_id
    message.sensor_type = sensor_type
    message.sensor_id = sensor_id
    message.param_name = name
    message.param_value = value

    main = instance.serviceManager.get('main')
    main.traverseDownMessage(device_id, message)
    return CR().response

@check_authcode
def get_sensor_status():
    """查询指定sensor设备的状态
    get /smartbox/sensor/status
    """
    authcode = request.values.get('authcode', '')
    device_ids = getAuthDeviceIds(authcode)

    device_id = request.values.get('id')
    sensor_id = request.values.get('sensor_id',0,type=int)
    sensor_type = request.values.get('sensor_type',0,type=int)

    if device_id not in device_ids:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    main = instance.serviceManager.get('main')
    # sensor = model.LogSensorStatus.get(device_id=device_id,sensor_id=sensor_id,sensor_type=sensor_type)
    sensor = model.Sensor.get(device_id=device_id,id=sensor_id,type=sensor_type)
    params = {}
    if sensor and sensor.params:
        params = json.loads(sensor.params)
    result=dict(device_id=device_id,sensor_type=sensor_type,sensor_id=sensor_id)
    if params:
        # result.update( sensor.dict())
        result.update(params)
    return CR(result=result).response


@check_authcode
def get_push_server():
    """获取推送服务器地址 TCP 流消息推送"""
    main = instance.serviceManager.get('main')
    host,port = main.getConfig().get('push_server').split(':')
    result = dict(server_host=host,server_port=int(port))
    return CR(result = result).response


def app_login_request():
    """1.8 App登录请求授权码

    """
    params = request.get_json()
    app_id = params.get('app_id')
    devices = params.get('devices',[])

    device_ids = map(lambda _:_['id'],devices)

    authcode = make_salt().upper()

    # authcode = 'A001'

    value = ','.join(device_ids)


    name = constants.AppRequestAuthCodeWidthIdsPrefix + authcode
    redis = instance.datasourceManager.get('redis')
    redis.conn.set(name,value)

    authdata = params
    authdata['create_time'] = int(time.time())
    name = constants.AppRequestAuthCodePrefix + authcode
    redis.conn.set(name, json.dumps(authdata),3600*24*20)

    return CR(result= authcode).response



"""


curl -H "Content-Type:application/json" -X POST http://127.0.0.1:9002/api/smartserver/authcode -d '{"app_id":"test","devices":[{"id":"FBXDDD0001"}]}'

curl  -X GET http://127.0.0.1:9002/api/smartbox/list?authcode=A001

curl  -X GET http://127.0.0.1:9002/api/smartbox/pushserver?authcode=A001

curl  -X GET http://127.0.0.1:9002/api/smartbox/profile?authcode=A001&id=FBXDDD0001

curl  -X GET http://127.0.0.1:9002/api/smartbox/status?authcode=A001&id=FBXDDD0001

curl  -X GET http://127.0.0.1:9002/api/smartbox/sensor/status?authcode=A001&id=FBXDDD0001


curl  -X POST http://127.0.0.1:9002/api/smartbox/sensor/status/query -d 'authcode=A001&id=FBXDDD0001'

curl  -X POST http://127.0.0.1:9002/api/smartbox/sensor/params -d 'authcode=A001&id=FBXDDD0001&sensor_id=1&sensor_type=2&name=brightness&value=10'

curl  -X POST http://127.0.0.1:9002/api/smartbox/params -d 'authcode=A001&id=FBXDDD0001&name=brightness&value=10'


authcode: A96FF8307DC84BE1A2FC31E28A53715F

"""