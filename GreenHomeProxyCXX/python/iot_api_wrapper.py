#coding:utf-8

"""
@brief:  huawei iot sdk 接口封装
@author: scott  24509826@qq.com
@date: 2018/12/18


"""

from ctypes import *
_lib = cdll.LoadLibrary('libuspsdk.so')


""""
typedef struct stru_ST_IOTA_DEVICE_INFO
{
    HW_CHAR *pcNodeId;
    HW_CHAR *pcName;
    HW_CHAR *pcDescription;
    HW_CHAR *pcManufacturerId;
    HW_CHAR *pcManufacturerName;
    HW_CHAR *pcMac;
    HW_CHAR *pcLocation;
    HW_CHAR *pcDeviceType;
    HW_CHAR *pcModel;
    HW_CHAR *pcSwVersion;
    HW_CHAR *pcFwVersion;
    HW_CHAR *pcHwVersion;
    HW_CHAR *pcProtocolType;
    HW_CHAR *pcBridgeId;
    HW_CHAR *pcStatus;
    HW_CHAR *pcStatusDetail;
    HW_CHAR *pcMute;
}ST_IOTA_DEVICE_INFO;
"""
class ST_IOTA_DEVICE_INFO(Structure):
	_pack_ = 8
	_fields_ = [
		('pcNodeId', c_char_p),
		('pcName', c_char_p),
		('pcDescription', c_char_p),
		('pcManufacturerId', c_char_p),
		('pcManufacturerName', c_char_p),
		('pcMac', c_char_p),
		('pcLocation', c_char_p),
		('pcDeviceType', c_char_p),
		('pcModel', c_char_p),
		('pcSwVersion', c_char_p),
		('pcFwVersion', c_char_p),
		('pcHwVersion', c_char_p),
		('pcProtocolType', c_char_p),
		('pcBridgeId', c_char_p),
		('pcStatus', c_char_p),
		('pcStatusDetail', c_char_p),
		('pcMute', c_char_p),
	]


"""
typedef struct stru_HW_MSG     { HW_INT unused; } * HW_MSG;
"""

class _HW_MSG(Structure):
	_pack_ = 8
	_fields_ = [
		('unused', c_int32),
	]

HW_MSG=POINTER(_HW_MSG)

"""
typedef HW_INT (*PFN_HW_BROADCAST_RECV)(HW_UINT uiCookie, HW_MSG pstMsg);
"""
PFN_HW_BROADCAST_RECV = CFUNCTYPE(c_uint32,)

"""
# HW_API_FUNC HW_INT HW_BroadCastReg(HW_CHAR *pcTopic, PFN_HW_BROADCAST_RECV pfnReceiver);
"""

HW_BroadCastReg = _lib.HW_BroadCastReg
HW_BroadCastReg.restype = c_int32
HW_BroadCastReg.argtypes = [c_char_p,PFN_HW_BROADCAST_RECV]

"""
# HW_API_FUNC HW_INT IOTA_Init(HW_CHAR *pcWorkPath, HW_CHAR *pcLogPath);
"""
IOTA_Init = _lib.IOTA_Init
IOTA_Init.restype = c_int32
IOTA_Init.argtypes = [c_char_p,c_char_p]

"""
# HW_API_FUNC HW_VOID IOTA_Destroy();
"""
IOTA_Destroy = _lib.IOTA_Destroy
IOTA_Destroy.restype = None
IOTA_Destroy.argtypes = []

"""
HW_API_FUNC HW_INT IOTA_ConfigSetStr(HW_INT iItem, HW_CHAR *pValue);
HW_API_FUNC HW_INT IOTA_ConfigSetUint(HW_INT iItem, HW_UINT uiValue);
"""
IOTA_ConfigSetStr = _lib.IOTA_ConfigSetStr
IOTA_ConfigSetStr.restype = c_int32
IOTA_ConfigSetStr.argtypes = [c_int32,c_char_p]


IOTA_ConfigSetUint = _lib.IOTA_ConfigSetUint
IOTA_ConfigSetUint.restype = c_int32
IOTA_ConfigSetUint.argtypes = [c_int32,c_uint32]


"""
HW_API_FUNC HW_INT IOTA_Bind(HW_CHAR *pcVerifyCode,ST_IOTA_DEVICE_INFO *pstInfo);
"""
IOTA_Bind = _lib.IOTA_Bind
IOTA_Bind.restype = c_int32
IOTA_Bind.argtypes = [c_char_p,POINTER(ST_IOTA_DEVICE_INFO)]


"""
HW_API_FUNC HW_INT HW_LogSetLevel(HW_UINT uiLogLevels);
"""
HW_LogSetLevel = _lib.HW_LogSetLevel
HW_LogSetLevel.restype = c_int32
HW_LogSetLevel.argtypes = [c_uint32]



"""
HW_API_FUNC HW_INT IOTA_Login();
HW_API_FUNC HW_INT IOTA_Logout();
"""
IOTA_Login = _lib.IOTA_Login
IOTA_Login.restype = c_int32
IOTA_Login.argtypes = []

IOTA_Logout = _lib.IOTA_Logout
IOTA_Logout.restype = c_int32
IOTA_Logout.argtypes = []


"""
HW_API_FUNC HW_INT HW_SysInit(HW_CHAR *pcWorkPath, HW_CHAR *pcLogFileName, HW_CHAR *pcVersion);
HW_API_FUNC HW_VOID HW_SysDestroy();
HW_API_FUNC HW_VOID HW_Sleep(HW_UINT uiSeconds);
"""
HW_SysInit = _lib.HW_SysInit
HW_SysInit.restype = c_int32
HW_SysInit.argtypes = [c_char_p,c_char_p,c_char_p]


HW_SysDestroy = _lib.HW_SysDestroy
HW_SysDestroy.restype = None
HW_SysDestroy.argtypes = []

HW_Sleep = _lib.HW_Sleep
HW_Sleep.restype = None
HW_Sleep.argtypes = [c_uint32]


"""
HW_API_FUNC HW_INT IOTA_ServiceDataReport(HW_UINT uiCookie, HW_CHAR *pcRequstId, 
            HW_CHAR *pcDeviceId, HW_CHAR *pcServiceId, HW_CHAR *pcServiceProperties);
"""
IOTA_ServiceDataReport = _lib.IOTA_ServiceDataReport
IOTA_ServiceDataReport.restype = c_int32
IOTA_ServiceDataReport.argtypes = [c_uint32,c_char_p,c_char_p,c_char_p,c_char_p]



class EN_IOTA_CFG_TYPE(object):
	EN_IOTA_CFG_DEVICEID     = 0 #平台分配的逻辑设备ID
	EN_IOTA_CFG_DEVICESECRET = 1 #设备接入的鉴权秘钥
	EN_IOTA_CFG_APPID        = 2 #开发者应用ID
	EN_IOTA_CFG_IOCM_ADDR    = 3 #IoCM服务器地址
	EN_IOTA_CFG_IOCM_PORT    = 4 #IoCM服务器端口
	EN_IOTA_CFG_MQTT_ADDR    = 5 #MQTT服务器地址
	EN_IOTA_CFG_MQTT_PORT    = 6 #MQTT服务器端口
	EN_IOTA_CFG_IODM_ADDR    = 7 #IoDM服务器地址
	EN_IOTA_CFG_IODM_PORT    = 8 #IoDM服务器端口


def test():
	import time
	# 注意： 必须保留 StartFunc(onStart) 的函数对象为全局，避免被GC回收导致回调异常


	server = '120.27.164.138'
	ip = '120.27.164.138'
	port = 7749
	username = 'test39-guest'

	time.sleep(10000)

if __name__ == '__main__':
	test()