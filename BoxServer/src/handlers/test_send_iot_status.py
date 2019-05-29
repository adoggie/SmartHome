#coding: utf -8

"""
应用平台向指定的设备发送状态消息
(redis 分发桥接)
"""
import json
import redis as Redis
import time
import iot_message

conn = Redis.StrictRedis(host='127.0.0.1', port=6379, password='', db=0)
name = 'FBXDDD0001'
def  send_iot_message():
    message = iot_message.IotMessageSensorDeviceStatusReport()
    message.device_id = name
    message.service_id = 'Light'
    message.sensor_type = 2
    message.sensor_id = 1
    message.status_data = json.dumps( dict(sensor_type = 2 , sensor_id=1, Switch=1) )
    conn.publish( name, message.marshall(''))


if __name__ == '__main__':
    for _ in range(100):
        send_iot_message()
        time.sleep(3)
