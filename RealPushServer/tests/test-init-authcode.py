# coding: utf-8

"""
模拟生成认证码和设备id列表
"""
import json
import time

from mantis.fundamental.redis.datasource import Datasource
from mantis.fanbei.smarthome.constants import AppRequestAuthCodeWidthIdsPrefix,AppRequestAuthCodePrefix
ds = Datasource()
ds.open()

authcode = 'A001'

name = AppRequestAuthCodeWidthIdsPrefix + authcode
ids =['FBXDDD0001']
value = ','.join(ids)
ds.conn.set(name,value)
print 'set value:',name,value

data = dict( app_id = 'app001' , device_ids=ids,create_time = int(time.time()) )

name = AppRequestAuthCodePrefix + authcode
ds.conn.set(name, json.dumps(data))
