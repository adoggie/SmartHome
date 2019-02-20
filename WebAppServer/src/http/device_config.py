#coding:utf-8
import json
import pymongo
from flask import Flask,request,g
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import ErrorReturn,CR
from mantis.fundamental.utils.timeutils import timestamp_current,datetime_to_timestamp,timestamp_to_str
from mantis.BlueEarth import model
from mantis.fundamental.utils.useful import object_assign

from mantis.BlueEarth.errors import ErrorDefs
from bson import ObjectId
from token import login_check,AuthToken


def get_device_config():
    """查询设备配置参数
    """
    user = g.user
    device_id = request.values.get('device_id')
    rel = model.DeviceUserRelation.get(user_id=user.id,device_id=device_id)
    device = model.Device.get(device_id=device_id)
    if not rel or not device:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response


    conf= model.DeviceConfig.get_or_new(device_id=device_id)
    result = conf.dict()
    result['device_name'] = rel.device_name
    result['imei'] = device.device_id
    result['sim'] = device.sim
    result['mobile'] = device.mobile

    return CR(result=result).response


def set_device_config():
    """设置设备配置参数
    """
    user = g.user
    device_id = request.values.get('device_id')
    data = request.values.to_dict()
    # for k,v in  request.args.items():
    #     data[k] = v



    conf = model.DeviceConfig.get_or_new(device_id=device_id)
    object_assign(conf,data)
    conf.server_port = int(conf.server_port)
    conf.gps_timer = int(conf.gps_timer)
    conf.lbs_timer = int(conf.lbs_timer)
    conf.heartbeat_timer = int(conf.heartbeat_timer)
    conf.battery_alarm_enable = int(conf.battery_alarm_enable)
    conf.shake_alarm_enable = int(conf.shake_alarm_enable)
    conf.sos_alarm_enable = int(conf.sos_alarm_enable)
    conf.fence_alarm_enable = int(conf.fence_alarm_enable)
    conf.gps_enable = int(conf.gps_enable)
    conf.lbs_enable = int(conf.lbs_enable)
    conf.wifi_enable = int(conf.wifi_enable)
    conf.fly_enable = int(conf.fly_enable)

    conf.save()

    # return CR().response

    device = model.Device.get(device_id=device_id)
    main = instance.serviceManager.get('main')
    cmds =[]
    cc = main.getCommandController(device.device_type)
    # cmd = ''
    # if 'server_mode' in request.values.keys():
    #     address = request.values.get('server_ip', '')
    #     port = request.values.get('server_port', 0)
    #     server_mode = request.values.get('server_mode','').lower()
    #     if  server_mode == 'ip':
    #         cmd = cc.setIpServer(address,port)
    #     elif server_mode =='domain':
    #         cmd = cc.setDomainServer(address,port)
    #
    # if cmd :  cmds.append(cmd)
    # cmd = ''
    # pos_mode = request.values.get('pos_mode')
    # if pos_mode == 'smart':
    #     cmd = cc.setPositionModeSmart()
    # elif pos_mode == 'timing':
    #     cmd = cc.setPositionModeTiming()
    #
    # if cmd: cmds.append(cmd)
    #
    # gps_timer = request.values.get('gps_timer')
    # lbs_timer = request.values.get('lbs_timer')
    #
    # cmd = ''
    # heartbeat_timer = request.values.get('heartbeat_timer')
    # if heartbeat_timer:
    #     cmd = cc.setHeartBeat(heartbeat_timer)
    # if cmd: cmds.append(cmd)
    #
    # # battery
    # cmd = ''
    # battery_alarm_enable = request.values.get('battery_alarm_enable')
    # if battery_alarm_enable =='1':
    #     cmd = cc.enableBatteryAlarm()
    # if battery_alarm_enable =='0':
    #     cmd = cc.disableBatteryAlarm()
    # if cmd: cmds.append(cmd)
    #
    # # sos
    # cmd = ''
    # sos_alarm_enable = request.values.get('sos_alarm_enable')
    # if sos_alarm_enable =='1':
    #     cmd = cc.enableSosAlarm()
    # if sos_alarm_enable =='0':
    #     cmd = cc.disableSosAlarm()
    # if cmd: cmds.append(cmd)
    #
    # # fence
    # cmd = ''
    # fence_alarm_enable = request.values.get('fence_alarm_enable')
    # if fence_alarm_enable == '1':
    #     cmd = cc.enableFenceAlarm()
    # if fence_alarm_enable == '0':
    #     cmd = cc.disableFenceAlarm()
    # if cmd: cmds.append(cmd)

    # sos
    cmd =''
    sos_1 = request.values.get('sos_1')
    sos_2 = request.values.get('sos_2')
    sos_3 = request.values.get('sos_3')
    # sos_4 = request.values.get('sos_4')
    if sos_1:
        conf.sos_1 = sos_1
    if sos_2:
        conf.sos_2 = sos_2
    if sos_3:
        conf.sos_3 = sos_3

    conf.save()

    args = filter(lambda _:_,(conf.sos_1,conf.sos_2,conf.sos_3))
    if args:
        cmd = cc.setSos(*args)
    if cmd: cmds.append(cmd)

    # send all out
    for cmd in cmds :
        main.sendCommand(device_id, cmd)

    return CR().response
