

接口设计
======

    auth : scott 
    date : 2019.2
    ver: 0.1

## 说明：
智能家居控制主机smartbox由Arm主机和STM单片机组成。
ARM主机负责对STM设备的控制管理，在STM设备与平台之间进行数据的交换传输。
STM设备通过多种通信接口对智能设备进行数据采集和控制。




stm32 使用 json 

[kiel-c json](https://blog.csdn.net/yannanxiu/article/details/52712723)



## 定义

* SmartBox  - 智能家居控制主机设备(包含: 上位和下位设备)
* Host - 主机的ARM主控模块，对STM来讲是上位系统，反之STM为下位系统 
* SensorHub -   STM单片机控制单元(传感器集线器)，完成各种传感设备数据采集和控制
* BoxServer -  接入BoxHost的云端通信服务模块，接收SmartBox的上行数据并下发控制命令

## 1. 主机与MCU
**( Host <-> SensorHub )**

> UART通信，波特率 115200 。 

####  传输

**编码:** 


    encoded_data = hex( data + crc16(data) )
        
    '123213' => '313233323133'


**封包:**

> 将设备的状态信息和控制命令组装到 `消息报文(P)` , 发送报文`P`时需添加报文分隔符 `\n`

    P1\nP2\nP3\n...
    
    send(P+'\n') 

消息接收端视`\n`为完整消息报文的结束符，将提取出的报文`P`末端2字节，并对之前的字节进行校验 `crc16`计算。

    data = bin(P[:-2]) 
    if crc ( data ) == P[-2:]:
        parse(data)  报文合法，处理报文内容


### 报文类型
> MessageType

| Name | Value | Direction | Comment |
| :--- | :---: | --- | --- |
| QueryDeviceCapacities | A1 | host->hub | 主机发送设备功能查询 |
| QueryDeviceValue | A2 | host->hub | 主机发送设备参数 |
| SetDeviceValue | A3 | host->hub | 主机发送设备功能查询 |
| SetSensorValue | A5 | host->hub | 设置设备参数 |
| QuerySensorValue | A6 | host->hub | 设置设备参数 |
| DeviceValueReport | B1 |  hub -> host | SensorHub上报设备功能 |
| DeviceStatusReport | B2 | hub -> host | SensorHub上报设备功能 |
| SensorValueReport | B3 | hub -> host | SensorHub上报设备运行状态 |


### SensorHub 参数值

| Name | Value |  Comment |
| :--- | :---: |  --- |
| ModeSave | 1 | 保存当前模式 | 
| ModeActive | 1－4 | 激活当前模式 | 


### SensorHub 状态值

| Name | Value |  Comment |
| :--- | :---: |  --- |
| Mode | 1-4 | 当前模式 | 
| Ver | str | 版本 | 
| Last | str | 启动时间 |
| Time | str | 当前时间 | 








### 报文格式

#### 1. Host  >> SensorHub
| Name | Value |  Comment |
| :--- | :---: |  --- |
| MessageType | b | 消息类型 | 
| SensorType | 1..n | mod设备类型  | 
| SensorIndex | 1..n | mod设备编号 | 
| ParamName | any | 名称 | 
| ParamValue | any | 值 |

报文内容采用明文编码，字段之间`,`为分隔符

样例:



	3,1,

###  传感器类型

| Name | Value |  Comment |
| :--- | :---: |  --- |
| Light | 0x01 | 灯光 | 
| | b |  | 


-----
### 传感设备参数规格

* TypeId : 设备类型
* Index : 设备编号
* Feature:
    - **id :**    (1:switch, 2:regulator,..)
    - **access :** (1: r , 2: w)
    - value_type:   1 - 枚举.   ;  2 - 范围       
    - value_range :  ("0-1-3","[1-100)" )


```    
    {   TypeId,Index,
        Features:[
            {id,access,value_type,value_range},
            ..
        ]
    }
```    

 
------

        

### 1.1 ReportDeviceCapacities
> SensorHub 上报设备功能清单

| Name | Value |  Comment |
| :--- | :---: |  --- |
| Type | ReportDeviceCapacities | c | 
| SensorType | b |  | 
