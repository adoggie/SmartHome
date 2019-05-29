
BoxServer
========
智能家庭控制主机的云端通信接入服务器

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