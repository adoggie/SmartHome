
### 设备定义
端点设备(sensor 或 endpoint) 的智能化管理可能包括两种基本的行为： 
1. 状态查询  status query
2. 命令控制  command execute 

### 端设备唯一标识: 

* sensor_id  整数值 （0 - N) 
* sensor_type 对应不同智能设备类型值( 0 - N )

id + type 组合端设备的唯一标识，也是智能主机访问外围智能设备的唯一标识号。 


### 端设备的行为操作

##### 1. 状态查询
控制者发送  查询请求，携带 sensor_id + sensor_type 到智能主机，智能主机一次返回多个k,v 状态值, 例如： 

```bash
{


}
```

#### 2. 控制
对端设备的控制主要有若干类型:
1. 开、关
2. 指定值 ( 整型 、浮点型 )
3. 最大（最高) 
4. 最小 (最低)
5. 步增
6. 步减

不同类型的端设备有多个不同的控制项，应根据设备类型分别进行定义。 

例如: 灯设备 的控制项
* 开关 
* 亮度
* 颜色

```json

```

##### 2.1 开、关

```json




```