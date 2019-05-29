
GreenHomeProxyCXX
========
C++版本的绿城家接入代理服务

## 主体功能

Proxy对象是实体SmartBox在云端Cloud的虚拟设备，每一台物理设备均运行独立的Proxy对象。

Proxy集成 华为IoT的设备SDK，实现在SmartCloud平台与绿城家平台的设备通信双向传输和处理。


## 环境&开发

    boost1.59
    jsoncpp
    redis-plusplus
     
## 流程设计

Proxy扮演物理设备SmartBox对接华为IoT接入的网关服务,SmartCloud::BoxServer负责接入Box设备到云平台。
BoxServer与Proxy之间通过Redis的Pub/sub进行消息的交换。
 
## 启动输入

1. 设备编号
2. 接入服务器的消息接收地址  
    > smartbox_message_chan_iot
3. redis服务器地址和端口    

```bash
./greenplus-agent --id=AX001 --redis=127.0.0.1:6379 --post=smartbox_message_chan_iot --datapath=/var/smartbox/iot
参数：
 id  设备硬件编号
 redis 投递消息服务
 post 投递消息队列
 datapath 设备相关数据存储目录（proxy运行期间存储过程数据)
```

## 设备数据目录

```
AX00x - 设备硬件编码

/var/green/
  - FAX001
    - gateway.txt
    - runtime.txt
  - settings.txt

```

## huawei Iot 接口定义
创建新的产品类型，不同的智能设备作为 service 对象分别加入 产品中， 每个 service都具有 type和id用于识别唯一。 

每个service下辖又配置多个控制命令 command.

```bash
product
 - service  (light,player,...)
    - attributes 
        ( switch, brightness, color ,..)
    - command 
        (switch , value , up , down )
```



## 开发技术资源

redisplusplus

https://blog.csdn.net/zyd_15221378768/article/details/79621676
