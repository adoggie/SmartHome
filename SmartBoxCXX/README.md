
SmartBoxCXX
========
C++版本的智能家庭控制主机程序

## 主体功能

1. 
2. 
3. 

## 环境&开发

    boost1.59
    jsoncpp 



## Test Scripts

```bash

wget http://127.0.0.1:7001/api/smartbox/sensor/status/generate?sensor_type=2&sensor_id=1&name=1&value=1


curl -X POST http://127.0.0.1:7001/api/smartbox/sensor/params -d 'sensor_type=1&sensor_id=2&name=light&value=on'
curl -X POST http://127.0.0.1:7001/api/smartbox/sensor/params -d 'sensor_type=1&sensor_id=2&name=1&value=1'
telnet 127.0.0.1 7002

```