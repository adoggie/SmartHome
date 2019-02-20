#coding:utf-8
import json
import pymongo
from flask import Flask,request,g
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from mantis.fundamental.flask.webapi import ErrorReturn,CR
from mantis.fundamental.utils.timeutils import timestamp_current,datetime_to_timestamp,timestamp_to_str
from mantis.BlueEarth import model
from mantis.fundamental.utils.useful import object_assign

from mantis.BlueEarth.errors import ErrorDefs
from bson import ObjectId
from token import login_check,AuthToken

def create_cargo_address():
    """查询本人创建的共享设备信息
        支持 共享设备编号查询 或 设备编号查询
        如果共享记录未创建则创建，并返回
    """
    user = g.user
    name = request.values.get('name')
    phone = request.values.get('phone')
    address_ = request.values.get('address','')
    is_default = request.values.get('is_default',0,type=int)
    if not name or not phone or not address_ :
        return ErrorReturn(ErrorDefs.ParameterInvalid,u'必须提供联系人、手机号、收件地址').response
    if is_default:
        # 将其他记录设置为非默认
        model.CargoAddress.collection().update_many({'user_id':user.id,'is_default':1},{'$set':{'is_default':0}})
    address = model.CargoAddress()
    address.user_id = user.id
    address.name = name
    address.phone = phone
    address.address = address_
    address.is_default = is_default
    address.order = timestamp_current()
    address.update_time = timestamp_current()
    address.save()

    return CR(result=address.id).response

def get_cargo_address_list():
    """查询本人创建的共享设备信息
        支持 共享设备编号查询 或 设备编号查询
        如果共享记录未创建则创建，并返回
    """
    user = g.user
    address_list = model.CargoAddress.collection().find({'user_id':user.id}).sort('order',pymongo.ASCENDING)
    result = []
    for address in list(address_list):
        object = model.CargoAddress()
        object_assign(object,address)
        result.append(object.dict())
    return CR(result=result).response


def get_cargo_address():
    """查询本人创建的共享设备信息
        支持 共享设备编号查询 或 设备编号查询
        如果共享记录未创建则创建，并返回
    """
    user = g.user
    id = request.values.get('id')
    address = model.CargoAddress.get(user_id=user.id,_id=ObjectId(id))
    if not address:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'地址对象不存在').response
    result = address.dict()
    return CR(result=result).response

def update_cargo_address():
    """
    """
    user = g.user
    id = request.values.get('id')
    is_default = request.values.get('is_default',0,type=int)
    order = request.values.get('order',0,type=int)
    props = request.values.to_dict()
    address = model.CargoAddress.get(_id=ObjectId(id))
    if not address:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'请求对象不存在').response
    object_assign(address,props)
    address.is_default = is_default
    address.user_id = user.id
    address.update_time = timestamp_current()
    address.save()
    return CR(result=address.id).response

def remove_cargo_address():
    """
    """
    user = g.user
    id = request.values.get('id')
    address = model.CargoAddress.get(_id = ObjectId(id))
    if not address:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'对象不存在').response
    address.delete()
    return CR(result=address.id).response