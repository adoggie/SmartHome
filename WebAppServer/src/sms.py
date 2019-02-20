#coding:utf-8

import  uuid, json
from mantis.fundamental.application.app import instance
from mantis.fundamental.aliyun import sms

def send_sms(phones,signature,template,**kwargs):
    main = instance.serviceManager.get('main')
    sms_cfgs = main.getConfig().get('sms')
    ak = sms_cfgs.get('ak')
    secrect = sms_cfgs.get('secret')
    sign = sms_cfgs.get('signatures').get(signature)
    template = sms_cfgs.get('templates').get(template)
    business_id = uuid.uuid1()
    params = json.dumps(dict(kwargs))
    ret =  sms.send_sms(ak,secrect,business_id, phones, sign,template, params)
    return ret

# def request_device_password(device_id):
#     """找回设备的管理密码"""

