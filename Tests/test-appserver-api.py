#coding:utf-8

"""
test-appserver-api.py
测试设备状态查询和设置，查询接入pushserver服务器和设备信息

"""

import sys,time,datetime,os,os.path,traceback,json

import requests


HOST='http://wallizard.com:9002'
# HOST='http://127.0.0.1:9002'
AuthCode = 'A001'

apis={
    'getDeviceList':{'url':'/api/smartbox/list','data':dict(authcode=AuthCode)
                     },

}

# 获取设备列表
def test_getdevice_list():
    data = dict(authcode=AuthCode)
    res = requests.get(HOST+'/api/smartbox/list',data).json()
    print res
    return res['result']

# 获取推送服务器连接地址
def test_get_pushserver():
    data = dict(authcode=AuthCode)
    res = requests.get(HOST + '/api/smartbox/pushserver', data).json()
    print res
    return res['result']

# 获取设备描述信息
def test_get_profile(device_id):
    data = dict(authcode=AuthCode,id=device_id)
    res = requests.get(HOST + '/api/smartbox/profile', data).json()
    print res
    return res['result']

# 查询设备当前运行状态
def test_get_device_status(device_id):
    data = dict(authcode=AuthCode,id=device_id)
    res = requests.get(HOST + '/api/smartbox/status', data).json()
    print res
    return res['result']

# 设置设备运行参数
def test_set_device_params(device_id):
    data = dict(authcode=AuthCode,id=device_id ,name='color',value=1)
    res = requests.post(HOST + '/api/smartbox/params', data).json()
    print res

# 获取设备端点设备的状态值
def test_get_sensor_status(device_id,sensor_type,sensor_id):
    data = dict(authcode=AuthCode, id=device_id, sensor_type=sensor_type, sensor_id=sensor_id)
    res = requests.get(HOST + '/api/smartbox/sensor/status', data).json()
    print res

# 设置端设备参数
def test_set_sensor_params(device_id,sensor_type,sensor_id,name,value):
    data = dict(authcode=AuthCode, id=device_id,
                sensor_type=sensor_type, sensor_id=sensor_id,
                name = name, value=value)
    res = requests.post(HOST + '/api/smartbox/sensor/params', data).json()
    print res

def test_get_authcode():
    data = dict(app_id='abc', devices=[
        {'id':'Fdx001111','name':'xxxx'}
    ])
    res = requests.post(HOST + '/api/smartserver/authcode', json=data).json()
    print res



if __name__ == '__main__':


    # ids = test_getdevice_list()
    # test_get_pushserver()
    # device_id = ids[0]['id']
    #
    # test_get_device_status(device_id)
    #
    # test_get_profile(device_id)
    # test_set_device_params(device_id)
    # test_get_sensor_status(device_id,2,1)
    # test_set_sensor_params(device_id,2,1,2,2)

    test_get_authcode()
