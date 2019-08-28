#coding:utf-8

# rokid 设备接口定义与转换

# import sensor_defs

import json,urllib2,urllib,os.path

def get_local_ip():
    return '192.168.14.17'

#  https://developer.rokid.com/docs/rokid-homebase-docs/v1/device/type.html

table_device_type = {
    2 : "light",
    1 : "curtain",
    3 : "ac"
}

table_features_type = {
    'switch':'switch',  # 右侧为rokid的 action 类型名
    'color':'color',
    'brightness':'brightness',
}

# left: rokid , right: fanbei
table_command_type = {
    'max':'max',
    'min':'min',
    'up':'up',
    'down':'down',
    'on':'on',
    'off':'off'

}

def get_device_profile_data():
    # f = open('profile.json')
    url = os.path.join( os.path.dirname( os.path.abspath(__file__) ),'profile-rokid.json')
    f = open(url)
    data = json.load(f)
    f.close()
    return data

def get_device_uid():
    uid = 'AAA'
    return uid

def parse_device_uid(uid):
    """分解出 device_id,sensor_type,sensor_id"""
    return uid.split('-')

def get_device_list():
    """转换profile为 rokid识别的格式"""
    result = []
    defines={}

    profile = get_device_profile_data()
    for item in profile["sensor_defines"]:
        defines[item["type"]] = item

    for sensor  in profile.get("sensors"):
        type_ = sensor['type']
        id_ = sensor['id']
        uid = "{}-{}-{}".format(get_device_uid(),type_, id_)
        type_info = defines[type_]
        room_id = sensor["room_id"]

        device = dict( type= table_device_type[type_] ,
                       deviceId = uid,
                       name = sensor['name'],
                       roomName = profile['rooms'].get(room_id,{}).get("name",''),
                       homeName = profile['house'].get('name','Family'),
                       actions ={},
                       state = {}
                       )
        for name,detail in type_info['features'].items():
            name = table_features_type[name]
            value_type_name = detail['value_type']['name']
            if value_type_name == 'enum':
                device['actions'][name] = detail['value_type']['items']
                device['state'][name] = detail['value_type']['default']
            else:
                device['actions'][name] = ['num']
                device['state']['name'] = detail['value_type']['default']


        result.append(device)
    return result


"""
https://developer.rokid.com/docs/rokid-homebase-docs/connect/http-remote-driver.html
https://developer.rokid.com/docs/rokid-homebase-docs/v1/device/actions-and-state.html#%E6%B8%A9%E5%BA%A6-temperature

"""
def translate_and_send_command(command):
    device = command.get('device',{})
    device_id = device.get('deviceId')
    _,sensor_type,sensor_id = parse_device_uid(device_id)
    action = command.get('action',{})
    prop = action.get('property')
    name = action.get('name')
    value = action.get('value')  # 只有指定'num' 才有value

    profile = get_device_profile_data()

    defines = profile.get('sensor_defines')

    for df in defines:
        if df.get('type') != int(sensor_type) : # 找到端设备类型
            continue
        feature = df.get('features').get(prop) # 找到对应的feature
        feature_id = feature.get('id')
        feature_value = ''
        name = table_command_type.get(name) # rokid -> fanbei
        if name == 'num': # 直接参数值设置 , value 有意义
            feature_value = value
        else:
            feature_value = feature.get('commands').get(name).get('value')
        # 发送到 smarbox的http api
        print 'send command to smartbox..'
        # return
        send_command(sensor_type,sensor_id,feature_id,feature_value)


def send_command(sensor_type,sensor_id,name,value):
    header_dict = {"Content-Type": "application/json"}
    data = {'sensor_type': sensor_type, 'sensor_id': sensor_id , 'name':name, 'value':value}
    url = 'http://{}:{}/api/smartbox/sensor/params'.format(SMARTBOX_IP,SMARTBOX_PORT)
    text = urllib.urlencode(data)
    req = urllib2.Request(url=url, data=text, headers=header_dict)
    res = urllib2.urlopen(req)
    res = res.read()
    print text
    # print res


# SMARTBOX_IP = '192.168.14.17'
SMARTBOX_IP = '127.0.0.1'
SMARTBOX_PORT = 7001

if __name__ == '__main__':
    import os.path
    print os.path.join( os.path.dirname( os.path.abspath(__file__) ),'profile-rokid.json')
    # print get_device_list()
