#coding:utf-8

import json
from flask import Flask,request,g
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from mantis.fundamental.application.app import instance
from mantis.fundamental.flask.webapi import ErrorReturn,CR
from mantis.fundamental.utils.timeutils import timestamp_current,datetime_to_timestamp,timestamp_to_str
from mantis.BlueEarth import model

from mantis.BlueEarth.errors import ErrorDefs
from bson import ObjectId

def create_share_device():
    """创建设备共享
        url: /share-device
        post
    """
    user = g.user
    device_id = request.values.get('device_id')
    name = request.values.get('name')
    expire = request.values.get('expire')   # 过期时间
    password = request.values.get('password','')
    user_limit = request.values.get('user_limit',0,type=int)
    status = request.values.get('status','open')

    #1.设备是否存在
    #2.是否已创建共享设备
    rel = model.DeviceUserRelation.get(user_id = user.id,device_id=device_id)
    if not rel:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'设备不存在').response

    link = model.SharedDeviceLink.get(user_id=user.id, device_id=device_id)
    if  link and link.name == name:
        return ErrorReturn(ErrorDefs.ObjectHasExist,u'名称重复，请重新填写').response
    if not password :
        password  = ''

    link = model.SharedDeviceLink()
    link.user_id = user.id
    link.open_id = user.account
    link.device_id = device_id
    link.device_type = rel.device_type
    link.name = name
    link.expire_time = expire
    link.password = password.strip()
    link.user_limit = user_limit
    link.create_time = timestamp_current()
    link.status = status
    link.save()

    return CR(result=link.id).response



def update_share_device():
    """更新共享设备信息"""
    user = g.user
    share_id = request.values.get('share_id')


    name = request.values.get('name')
    expire = request.values.get('expire')  # 过期时间
    password = request.values.get('password', '')
    user_limit = request.values.get('user_limit', 0, type=int)
    status = request.values.get('status','')

    if status  not in ('open','close'):
        return ErrorReturn(ErrorDefs.ParameterInvalid,u'提交参数错误').response
    link = model.SharedDeviceLink.get(user_id=user.id, _id=ObjectId(share_id))
    if not  link:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    if not password:
        password = ''

    link.name = name
    link.expire_time = expire
    link.password = password.strip()
    link.user_limit = user_limit
    link.status = status
    link.save()
    return CR(result='').response


# def get_share_device_access_user():
#     """共享设备的访问用户信息
#     """
#
#     user = g.user
#     share_id = request.values.get('share_id')
#     user_id = request.values.get('user_id')
#     # 此用户是否存在共享设备
#     link = model.SharedDeviceLink.get(user_id=user.id, _id=ObjectId(share_id))
#     if not link:
#         return ErrorReturn(ErrorDefs.ObjectNotExist).response
#     # 找到共享设备相关的用户
#
#     user = model.DeviceUserRelation.get(user_id=user_id, is_share_device=True, share_device_link=share_id)
#     if not user:
#         return ErrorReturn(ErrorDefs.ObjectNotExist).response
#     data = dict(
#         user_id=user.id,
#         wx_user=user.wx_user,
#         name=user.name,
#         avatar=user.avatar,
#         mobile=user.mobile,
#         account=user.account
#     )
#     return CR(result=data).response
#
#
# # /share-device/access-user/list
# def get_share_device_access_user_list():
#     """查询指定共享设备关联的所有访问用户记录
#     """
#     user = g.user
#     share_id = request.values.get('share_id')
#
#     # 此用户是否存在共享设备
#     link = model.SharedDeviceLink.get(user_id=user.id, _id=ObjectId(share_id))
#     if not link:
#         return ErrorReturn(ErrorDefs.ObjectNotExist).response
#     # 找到共享设备相关的用户
#     users = []
#     rels = model.DeviceUserRelation.find(is_share_device=True, share_device_link=share_id)
#     for rel in rels:
#         user = model.User.get(_id=ObjectId(rel.user_id))
#         if not user:
#             continue
#         data = dict(
#             user_id=user.id,
#             wx_user=user.wx_user,
#             name=user.name,
#             avatar=user.avatar,
#             mobile=user.mobile,
#             account=user.account
#         )
#         users.append(data)
#
#     return CR(result=users).response


def get_device_share_info():
    """查询本人创建的共享设备信息
        支持 共享设备编号查询 或 设备编号查询
        如果共享记录未创建则创建，并返回
    """
    user = g.user
    share_id = request.values.get('share_id')
    # device_id = request.values.get('device_id')

    link = None
    # if share_id:
    #     link = model.SharedDeviceLink.get(user_id=user.id,_id=ObjectId(share_id))
    # device = model.DeviceUserRelation.get(user_id=user.id, device_id=device_id)
    # if not device:
    #     return ErrorReturn(ErrorDefs.ObjectNotExist,u'设备对象不存在').response

    # link = model.SharedDeviceLink.get(user_id=user.id,device_id=device_id)
    link = model.SharedDeviceLink.get(_id=ObjectId(share_id))

    result = link.dict()
    result['share_id'] = link.id
    result['create_time_str'] = timestamp_to_str(result['create_time'])

    expire_time = parse(link.expire_time) + relativedelta(days=+1)
    expire_time = datetime_to_timestamp(expire_time)
    # 共享设备是否过期
    if expire_time and expire_time < timestamp_current():
        result['is_expired'] = True

    # 访问上限
    if link.user_limit:
        num = model.DeviceUserRelation.collection().find({'share_device_link': link.id}).count()
        if num >= link.user_limit:
            result['is_limited'] = True

    if link.password:
        result['is_password_null'] = False
    else:
        result['is_password_null'] = True

    return CR(result=result).response



def get_share_device_list():
    """查询本人创建的所有共享设备列表
        支持查询某一台设备的共享列表
    """
    user = g.user
    device_id = request.values.get('device_id')

    links = []
    # device_id =''
    if device_id:
        links = model.SharedDeviceLink.find(user_id=user.id,device_id=device_id)
    else:
        links = model.SharedDeviceLink.find(user_id=user.id)

    result=[]
    for link in links:

        data = link.dict()
        data['share_id'] = link.id
        data['create_time_str'] = timestamp_to_str(data['create_time'])
        result.append(data)
    return CR(result=result).response


def get_share_device_follower_list():
    """获取关注位置设备的好友
        GET /share-device/follower/list
    """
    user = g.user
    share_id = request.values.get('share_id')
    share = model.SharedDeviceLink.get(_id = ObjectId(share_id))
    if not share:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    followers = model.ShareDeviceFollower.find(share_id = share_id)
    result = {}
    result['share'] = share.dict()
    result['followers'] = []
    for follower in followers:
        wxuser = model.WxUser.get(open_id=follower.open_id)
        if wxuser:
            follower.avatar_url = wxuser.avatarUrl
            follower.nick_name = wxuser.nickName
            
        data = follower.dict()
        result['followers'].append(data)

    return CR(result=result).response

def share_device_follower_allow(denied=False):
    """ 允许follower访问设备
        GET /share-device/follower/allow
    """
    user = g.user
    follower_id = request.values.get('follower_id')
    follower = model.ShareDeviceFollower.get(_id = ObjectId(follower_id))
    if not follower:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response
    # 防止非法跨用户操作
    share = model.SharedDeviceLink.get(_id = ObjectId(follower.share_id),user_id= user.id)
    if not share:
        return ErrorReturn(ErrorDefs.ObjectNotExist).response

    follower.denied = denied
    follower.save()
    return CR().response

def share_device_follower_deny():
    """ 禁止 follower访问设备
        GET /share-device/follower/deny
    """
    return share_device_follower_allow(denied=True)


def remove_share_device():
    """删除设备共享, 共享发起人删除共享的设备，导致所有的共享连接失效
        删除共享设备的追随者 follower
    """
    user = g.user
    share_id = request.values.get('share_id')
    link = model.SharedDeviceLink.get(user_id=str(user.id), _id= ObjectId(share_id))
    if not link:  # 设备不存在
        return ErrorReturn(ErrorDefs.ObjectNotExist).response
    # 查找设备的分享链接
    coll = model.DeviceUserRelation.collection()
    coll.delete_many({'is_share_device': True, 'share_device_link': link.id})
    # 删除共享设备的followers
    coll = model.ShareDeviceFollower.collection()
    coll.delete_many({'share_id':share_id})
    link.delete()
    return CR().response

def take_share_device():
    """用户接收共享设备，添加成为自己的设备
        如果设置了密码，且用户未上传密码，则提示密码输入
        @:return 返回新设备id
    """
    user = g.user
    auth = g.auth

    share_id = request.values.get('share_id')
    password = request.values.get('password')
    link = model.SharedDeviceLink.get(_id = ObjectId(share_id))
    if not link:
        return ErrorReturn(ErrorDefs.ObjectNotExist,u'共享资源对象不存在').response

    # 共享设备是否是自己的设备(自己注册的或者之前分享来自他人的)
    rel = model.DeviceUserRelation.get(user_id =user.id,device_id = link.device_id)
    if rel:
        return ErrorReturn(ErrorDefs.ObjectHasExist,u'分享设备已存在').response

    expire_time = parse(link.expire_time) + relativedelta(days=+1)
    expire_time = datetime_to_timestamp(expire_time)
    # 共享设备是否过期
    if expire_time and expire_time < timestamp_current():
        return ErrorReturn(ErrorDefs.ResExpired,u'设备分享已过期').response

    # 访问上限
    if link.user_limit:
        num = model.DeviceUserRelation.collection().find({'share_device_link':link.id}).count()
        if num >= link.user_limit:
            return ErrorReturn(ErrorDefs.ReachLimit,u'分享已达到人数上限').response

    # 检测当前用户是否被阻止
    follower = model.ShareDeviceFollower.get(share_id = share_id,user_id=user.id)
    if follower and follower.denied:
        return ErrorReturn(ErrorDefs.AccessDenied,u'当前用户访问共享资源受限').response

    #是否要提供密码
    if link.password:
        if  password != link.password:
            return ErrorReturn(ErrorDefs.NeedPassword,u'需要提供分享访问密码').response
    #创建设备
    device = model.DeviceUserRelation()
    device.user_id = user.id
    device.device_id = link.device_id
    device.device_name = link.name
    device.update_time = timestamp_current()
    device.is_share_device = True
    device.share_user_id = link.user_id
    device.share_device_link = link.id
    device.save()
    #添加到分享者列表
    if not follower:
        follower = model.ShareDeviceFollower()
        follower.user_id = user.id
        follower.open_id = auth.open_id
        follower.share_id = link.id
        follower.device_id = device.id
        follower.create_time = timestamp_current()
        wxuser = model.WxUser.get(open_id=auth.open_id)
        if wxuser:
            follower.avatar_url = wxuser.avatarUrl
            follower.nick_name = wxuser.nickName
        follower.save()


    return CR(result= str(device.id) ).response


def create_share_device_code():
    """生成分享码
        缓存中记录分享码生成时间
    """
    from mantis.BlueEarth import constants
    redis = instance.datasourceManager.get('redis').conn
    code = '1212'
    name = constants.DeviceShareCodeCreateTimeKey.format(code)
    redis.set(name,timestamp_current(),3600)
    return CR(result=code).response