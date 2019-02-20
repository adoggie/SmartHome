
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
 