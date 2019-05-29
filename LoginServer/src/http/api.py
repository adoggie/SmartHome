#coding:utf-8

import json
from flask import Flask,request,g

from mantis.fundamental.application.app import  instance

from mantis.fundamental.flask.webapi import ErrorReturn,CR
from mantis.fundamental.utils.timeutils import timestamp_current
from mantis.fundamental.utils.useful import object_assign,hash_object
from mantis.fanbei.smarthome import model
from mantis.fanbei.smarthome.errors import ErrorDefs
from mantis.fanbei.smarthome.token import device_token_create

from mantis.fundamental.utils.signature import make_signature


"""

1. getServiceTime

Url: /smartserver/api/time/now
Method: GET
Request:
Response:
    time - 当前服务器时间戳


2. login
Url: /server/api/login
Method: POST
Request:
    id      - 设备编号
    type    - 设备类型
    ver         - 设备版本
    
    
    # time        - 当前时间
    # sign   - 签名    md5(screct_key + id+ type + ver + time )
    # 

Response:
    token           - 设备访问令牌
    server_ip       - 服务器地址
    server_port     - 服务器端口
    server_time     - 服务器时间

"""

def device_login():
    """设备主机登陆，服务器校验合法性，并返回接入服务器地址"""
    main = instance.serviceManager.get('main')
    id_ = request.values.get('id')
    type_ = request.values.get('type')
    ver = request.values.get('ver')
    time = request.values.get('time')
    sign = request.values.get('sign','').upper()


    if not id_ or not type_ or not ver or not time or not sign:
    # if not id_ or not type_ :
        return ErrorReturn(ErrorDefs.ParameterInvalid).response

    secret_key = main.getConfig().get('device_secret_key')

    value,_ = make_signature(secret_key,dict(id=id_,type=type_,ver=ver,time=time))
    if value != sign:
        instance.getLogger().error(u"数据签名计算错误")
        return ErrorReturn(ErrorDefs.ParameterInvalid).response

    device = model.SmartDevice.get(id = id_)
    if not device:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'设备不存在').response

    # 加入 认证处理时间
    data = dict(id=id_,type=type_,ver=ver,time=time,auth_time=timestamp_current())

    token = device_token_create(data,device.secret_key)
    server = model.DeviceServer.get(id=device.server_id)
    if not server:
        return ErrorReturn(ErrorDefs.DeviceServerNotFound).response

    result = dict( token = token, server_ip = server.ip, server_port = server.port ,
        server_time = timestamp_current()
    )

    return CR(result= result).response
