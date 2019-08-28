
AppServer
========
提供App访问查询控制远端box的访问webapi接口

## 主体功能

1. 设备的上线、下线、消息进行推送到前端客户(socket.io)
2. 设备的控制命令发送方式： 即时发送（设备在线）、延时发送（设备离线）
3. 

## 环境&开发

    python
    gevent 
    mongodb
    redis 

## 过程

1. settings.yaml 的 redis/datasource 配置接收来自 iot的消息队列  pubsub (iot_data_chan/handlers.iot.get_message)
2. 外部系统通过http的接口接收控制指令并下发到线下设备端


### 订阅通道

```json
   
"smartbox.subs.DEVICE-ID"
1. app 接收设备消息
2. 接入服务器转发设备状态消息


"DEVICE-ID"
1. iot 接收消息
2. 接入服务器转发设备状态消息   

```