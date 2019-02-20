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

"""
设备组管理接口
"""
@login_check
def get_group_list():
    """查询用户设备组列表
    """
    user = g.user
    limit = request.values.get('limit',9990,type=int)
    rs = model.Group.collection().\
        find( {'user_id':user.id}).sort([('order',pymongo.ASCENDING)]).limit(limit)
    result = []
    for r in list(rs):
        count = model.DeviceGroupRelation.collection().find({'group_id': str(r['_id'])}).count()

        r['device_count'] = count
        r['id'] = str(r['_id'])
        del r['_id']
        result.append(r)
    return CR(result=result).response

@login_check
def create_group():
    """创建设备组
    """
    user = g.user
    name = request.values.get('name')
    comment = request.values.get('comment','')

    if not name:
        return ErrorReturn(ErrorDefs.ParameterInvalid).response
    if model.Group.get(name=name):
        return ErrorReturn(ErrorDefs.ObjectHasExist,u'相同组名已存在').response

    group = model.Group()
    group.name = name
    group.comment = comment
    group.order = timestamp_current()
    group.user_id = user.id
    group.create_time = timestamp_current()
    group.update_time = timestamp_current()
    group.save()
    return CR(result=group.id).response

@login_check
def remove_group():
    """删除设备
    """
    user = g.user
    group_id = request.values.get('group_id')
    group = model.Group.get(_id=ObjectId(group_id),user_id=user.id)

    model.DeviceGroupRelation.collection().delete_many({'group_id': group_id})
    if not group:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response
    group.delete()


    return CR().response

@login_check
def get_group_info():
    """获取设备详情
    """
    user = g.user
    group_id = request.values.get('group_id')
    include_devices = request.values.get('include_devices',0,type = int)
    group = model.Group.get(_id=ObjectId(group_id), user_id=user.id)
    if not group:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response
    result = group.dict()

    if include_devices:
        result['devices'] = []
        rs = model.DeviceGroupRelation.collection().find( {'group_id': group_id }).sort([('order',pymongo.ASCENDING)])
        for rel in list(rs):
            # device = model.Device.get(device_id = rel.device_id)
            devrel = model.DeviceUserRelation.get(user_id = user.id,device_id = rel['device_id'])
            if devrel:
                data = dict(
                    device_id= devrel.device_id,
                    device_type = devrel.device_type,
                    name = devrel.device_name
                )
                result['devices'].append(data)
        result['device_count'] = len(result['devices'])
    return CR(result=result).response

@login_check
def update_group_info():
    """更新设备组信息
     支持记录 置顶 settop = 1
    """
    user = g.user
    group_id = request.values.get('group_id')
    name = request.values.get("name")
    comment = request.values.get('comment')
    settop = request.values.get('set_top',0,type=int)
    group = model.Group.get(user_id=user.id,_id=ObjectId(group_id))
    if not group:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response
    if name:
        group.name = name
    if comment:
        group.comment = comment
    if settop:
        group.order = -timestamp_current()

    if name or comment or settop:
        group.update_time = timestamp_current()
        group.save()

    return CR(result=group.id).response

@login_check
def add_device_into_group():
    """添加设备到组
    """
    user = g.user
    group_id = request.values.get('group_id')
    device_id = request.values.get('device_id')
    rel = model.DeviceGroupRelation.get(user_id = user.id,group_id=group_id,device_id=device_id)
    if rel:
        return CR().response
    rel = model.DeviceGroupRelation()
    rel.group_id = group_id
    rel.device_id = device_id
    rel.user_id = user.id
    rel.update_time = timestamp_current()
    rel.order = timestamp_current()
    rel.save()
    return CR(result=rel.id).response

@login_check
def remove_device_from_group():
    """删除设备到组
    """
    user = g.user
    group_id = request.values.get('group_id')
    device_id = request.values.get('device_id')
    rel = model.DeviceGroupRelation.get(user_id=user.id, group_id=group_id, device_id=device_id)
    if not rel:
        return CR().response
    rel.delete()
    return CR().response