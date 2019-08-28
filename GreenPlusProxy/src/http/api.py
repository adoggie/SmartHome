#coding:utf-8

import json
from flask import Flask,request
from flask import Response

from flask import render_template
from mantis.fundamental.application.app import  instance
from mantis.fundamental.flask.webapi import *
from mantis.fundamental.flask.utils import nocache
from mantis.BlueEarth.utils import sendCommand
from mantis.BlueEarth import model

def get_active_devices():
    """获取在线设备"""
    cr  =CR()
    main = instance.serviceManager.get('main')
    adapters = main.getActivedDevices()
    result=[]
    for adapter in adapters:
        device_id = adapter.device_id
        device_type = adapter.device_type
        device = model.Device.get(device_id=device_id)
        if device:
            item ={'device_id':device_id,'name':device.name,'device_type':device_type}
            result.append(item)
    cr.assign(result)
    return cr.response

def send_command():
    """获取在线设备,可控制是否设备离线发送还是在线发送"""
    main = instance.serviceManager.get('main')
    cr  =CR()
    print request.query_string
    device_id = request.values.get('device_id')
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


