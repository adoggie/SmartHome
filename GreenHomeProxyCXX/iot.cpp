//
// Created by scott on 2019/4/30.
//


#include "Controller.h"
#include "message.h"
#include "app.h"

#include <stdio.h>

#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>


#define BUFF_MAX_LEN              200
#define MAX_REQUEST_ID_POSTFIX    9999

HW_UINT HW_GeneralCookie() {
    static HW_UINT uiCookie = 0;

    return uiCookie++;
}

HW_VOID HW_GetUUID(HW_CHAR *pcUUID)
{
    static HW_UINT uiMsgIdHigh;
    static HW_UINT uiMsgIdLow;
    static HW_UINT uiMsgSeqHigh;
    static HW_UINT uiMsgSeqLow;

    srand((int)time(0));

    uiMsgIdHigh  = rand()| 0x80000000;
    uiMsgIdLow   = rand();
    uiMsgSeqHigh = rand();
    uiMsgSeqLow  = 0x3AC3A353;

    sprintf(pcUUID,"%04X%04X-%04X-%04X-%04X-%04X%04X%04X",
            uiMsgIdHigh, uiMsgIdLow,
            uiMsgSeqHigh++, rand(), uiMsgSeqLow++,
            rand(), rand(), rand());
    return;
}

HW_VOID HW_GetRequestId(HW_CHAR *pcRequestId)
{
    static HW_UINT mRequestIdPostFix = MAX_REQUEST_ID_POSTFIX;
    static HW_CHAR aszUUID[BUFF_MAX_LEN];

    if (HW_NULL == pcRequestId)
    {
        return;
    }

    if (mRequestIdPostFix < MAX_REQUEST_ID_POSTFIX)
    {
        mRequestIdPostFix++;
    }
    else
    {
        HW_GetUUID(aszUUID);
        mRequestIdPostFix = 1;
    }

    sprintf(pcRequestId,"%s_%04d",aszUUID,mRequestIdPostFix);
    return;
}

Config Controller::iot_load_device_config(){
    Config gateway;
    std::string datapath , filename ;
    datapath = cfgs_.get_string("datapath");
    filename = datapath + "/gateway.txt";
    gateway.load( filename);
    return gateway;
}

Config Controller::iot_load_runtime_config(){
    Config gateway;
    std::string datapath , filename ;
    datapath = cfgs_.get_string("datapath");
    filename = datapath + "/runtime.txt";
    gateway.load( filename);
    return gateway;
}


void Controller::iot_reset_runtime_config(){
    Config gateway;
    std::string datapath , filename ;
    datapath = cfgs_.get_string("datapath");
    filename = datapath + "/runtime.txt";
//    gateway.save( filename);
    ::remove( filename.c_str() );
}

void Controller::iot_save_runtime_config(Config & runtime){

    std::string datapath , filename ;
    datapath = cfgs_.get_string("datapath");
    filename = datapath + "/runtime.txt";
    runtime.save( filename);

}

bool Controller::iot_init(){
    std::string config_path;
    config_path = cfgs_.get_string("datapath");

    IOTA_Init((HW_CHAR*)config_path.c_str(), (HW_CHAR*)config_path.c_str());
    iot_register_broadcast();

    iot_bind_ok_ = false;
    return true;
}

bool Controller::iot_start(){

    Config runtime;
    runtime = iot_load_runtime_config();
    if(runtime.get_string("DeviceId") == ""){
        iot_bind_gateway();
        HW_Sleep(5);
    }else{
        iot_login();
    }
    return true;
}

bool Controller::iot_bind_gateway() {
    Config gateway;

    puts("Try to Device Binding..");
    gateway = iot_load_device_config();

    ST_IOTA_DEVICE_INFO  stDeviceInfo = {0};
//    uiPort = HW_JsonGetUint(json, IOTA_PLATFORM_PORT,8943);
    int port  = cfgs_.get_int("platformPort",8943);
    std::string platformAddr = cfgs_.get_string("platformAddr","100.115.140.30");

    stDeviceInfo.pcMac = (HW_CHAR *)gateway.get_string("mac").c_str();
    stDeviceInfo.pcNodeId = stDeviceInfo.pcMac;
    stDeviceInfo.pcManufacturerId = (HW_CHAR*) gateway.get_string("manufacturerId").c_str();
    stDeviceInfo.pcDeviceType = (HW_CHAR*) gateway.get_string("deviceType").c_str();
    stDeviceInfo.pcModel = (HW_CHAR*) gateway.get_string("model").c_str();
    stDeviceInfo.pcProtocolType =(HW_CHAR*) gateway.get_string("protocolType").c_str();
//    g_uiLogLevel = HW_JsonGetUint(json, IOTA_LOGLEVEL,0);
    HW_LogSetLevel(255);


    IOTA_ConfigSetStr(EN_IOTA_CFG_IOCM_ADDR,(HW_CHAR*) platformAddr.c_str());
    IOTA_ConfigSetUint(EN_IOTA_CFG_IOCM_PORT, port);
    IOTA_Bind(stDeviceInfo.pcMac, &stDeviceInfo);


    return true;
}

void Controller::iot_register_broadcast() {
    HW_BroadCastReg((HW_CHAR*)IOTA_TOPIC_BIND_RSP, Controller::iot_RegResultHandler); // bind response back
    HW_BroadCastReg((HW_CHAR*)IOTA_TOPIC_CMD_UNBIND_RECEIVE, Controller::Gateway_UnbindRecvtHandler);
    HW_BroadCastReg((HW_CHAR*)IOTA_TOPIC_CONNECTED_NTY, Controller::Device_ConnectedHandler);
    HW_BroadCastReg((HW_CHAR*)IOTA_TOPIC_DISCONNECT_NTY, Controller::Device_DisconnectHandler);
    HW_BroadCastReg((HW_CHAR*)IOTA_TOPIC_HUB_ADDDEV_RSP, Controller::Device_AddResultHandler);
    HW_BroadCastReg((HW_CHAR*)IOTA_TOPIC_HUB_RMVDEV_RSP, Controller::Device_RemovResultHandler);
    HW_BroadCastReg((HW_CHAR*)IOTA_TOPIC_DEVUPDATE_RSP, Controller::Device_DevUpDateHandler);
}

HW_INT Controller::iot_RegResultHandler(HW_UINT uiCookie, HW_MSG pstMsg){
    //绑定注册成功，回写注册信息用于下次登录
    HW_UINT uiRegRet;
    uiRegRet = HW_MsgGetUint(pstMsg, EN_IOTA_BIND_IE_RESULT, EN_IOTA_BIND_RESULT_FAILED);
    if (EN_IOTA_BIND_RESULT_SUCCESS != uiRegRet) {
        // 绑定失败
        HW_LOG_ERR((HW_CHAR*)"---------------- Reg failed ------------------ Result=%u.", uiRegRet);
        return HW_ERR;
    }
    //获取注册信息，ls写入持久化文件 runtime.txt
    Config runtime;
    runtime =Controller::instance()->iot_load_runtime_config();

    std::string pcDeviceId = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_DEVICEID);
    std::string pcDeviceSecret = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_DEVICESECRET);
    std::string pcAppId = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_APPID);
    std::string pcIoCMServerAddr = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_IOCM_ADDR);
    std::string pcMQTTServerAddr = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_MQTT_ADDR);
    std::uint32_t  pcIoCMServerport = HW_MsgGetUint(pstMsg, EN_IOTA_BIND_IE_IOCM_PORT,8943);
    std::uint32_t pcMQTTServerport = HW_MsgGetUint(pstMsg, EN_IOTA_BIND_IE_MQTT_PORT,8883);

    runtime.set_string("DeviceId" , pcDeviceId);
    runtime.set_string("DeviceSecret" , pcDeviceSecret);
    runtime.set_string("AppId" , pcAppId);
    runtime.set_string("IoCMServerAddr" , pcIoCMServerAddr);
    runtime.set_string("MQTTServerAddr" , pcMQTTServerAddr);
    runtime.set_int("IoCMServerport" , (int)pcIoCMServerport);
    runtime.set_int("MQTTServerport" ,(int) pcMQTTServerport);

    runtime.set_string( Controller::instance()->cfgs_.get_string("device_id"),pcDeviceId); //
    runtime.set_string(pcDeviceId, Controller::instance()->cfgs_.get_string("device_id")); //


    std::string filename ;
    filename = Controller::instance()->cfgs_.get_string("datapath")+ "/runtime.txt";
    runtime.save( filename );

    Controller::instance()->iot_bind_ok_ = true;
    Controller::instance()->iot_login();
    return 0;
}

bool Controller::iot_login(){
    // 设备登录
    std::string value ;
    std::string device_id;
    Config gateway;
    gateway = iot_load_runtime_config();

    device_id = gateway.get_string("DeviceId");
    IOTA_ConfigSetStr(EN_IOTA_CFG_DEVICEID, (HW_CHAR *)device_id.c_str());
    IOTA_ConfigSetStr(EN_IOTA_CFG_IOCM_ADDR, (HW_CHAR *)gateway.get_string("IoCMServerAddr").c_str());
    IOTA_ConfigSetStr(EN_IOTA_CFG_APPID, (HW_CHAR *)gateway.get_string("AppId").c_str());
    IOTA_ConfigSetStr(EN_IOTA_CFG_DEVICESECRET, (HW_CHAR *)gateway.get_string("DeviceSecret").c_str());
    IOTA_ConfigSetStr(EN_IOTA_CFG_MQTT_ADDR, (HW_CHAR *)gateway.get_string("MQTTServerAddr").c_str());
    IOTA_ConfigSetUint(EN_IOTA_CFG_MQTT_PORT, (HW_UINT )gateway.get_int("MQTTServerport"));
    IOTA_ConfigSetUint(EN_IOTA_CFG_IOCM_PORT, (HW_UINT )gateway.get_int("IoCMServerport"));


    value = IOTA_TOPIC_SERVICE_COMMAND_RECEIVE + std::string("/") + device_id;
    HW_BroadCastReg((HW_CHAR *) value.c_str(), Controller::Device_ServiceCommandReceiveHandler); // 命令接收

    value = std::string(IOTA_TOPIC_DATATRANS_REPORT_RSP) + "/" + device_id;
    HW_BroadCastReg((HW_CHAR*)value.c_str(), Controller::Device_ServiceDataReportResultHandler); //设备状态上报的回报响应
//    HW_LOG_INF("--------------- Reg DataReportResultHandler ----------------- acBuf=%s", acBuf);
    IOTA_Login();

    return true;
}


std::string Controller::get_iot_device_id(const std::string& device_id){
    std::string iot_id;
    Config runtime;
    runtime = iot_load_runtime_config();
    iot_id = runtime.get_string(device_id);
    return iot_id;
}

std::string Controller::get_device_id(const std::string& iot_id){
    std::string device_id;
    Config runtime;
    runtime = iot_load_runtime_config();
    device_id = runtime.get_string(iot_id);
    return device_id;
}

bool Controller::iot_device_status_update(const std::string& device_id, const std::string& status , const std::string& detail) {
    std::string iot_id;
    iot_id = get_iot_device_id( device_id);
    IOTA_DeviceStatusUpdate(HW_GeneralCookie(),(HW_CHAR*) iot_id.c_str(),(HW_CHAR*) status.c_str(), (HW_CHAR*)detail.c_str() );
    return true;
}

std::string Controller::get_device_id(const std::string& sensor_type, const std::string& sensor_id){
    return cfgs_.get_string("device_id") + "-" + sensor_type + "-" + sensor_id;
}

bool Controller::iot_device_data_report(const std::string& device_id, const std::string& service_id, const std::string& jsondata){
    HW_CHAR aszRequestId[BUFF_MAX_LEN];
    HW_GetRequestId(aszRequestId);
    if( !iot_logined_ ){  // 未登录
        return false;
    }

    std::string iot_id;
    iot_id = get_iot_device_id(device_id);
    if(iot_id == ""){
        return false;
    }
    IOTA_ServiceDataReport(HW_GeneralCookie(), aszRequestId, (HW_CHAR*)iot_id.c_str(), (HW_CHAR*)service_id.c_str(),
                           (HW_CHAR*) jsondata.c_str());

    return true;
}

// gateway 设备登录成功
HW_INT Controller::Device_ConnectedHandler(HW_UINT uiCookie, HW_MSG pstMsg) {
    HW_CHAR *pcJsonStr;

    HW_LOG_INF((HW_CHAR*)"--------------- ConnectedHandler gateway connected ----------------!");

    Controller::instance()->iot_logined_ = true;
//    g_uiLoginFlg = HW_TRUE;

//    Gateway_DataReport(&pcJsonStr);

    HW_Sleep(5);
    Controller::instance()->iot_device_data_report( Controller::instance()->cfgs_.get_string("device_id"),"Light","{\"Switch\":1,\"color\":5}");
    // discard hub device add in.
//    Controller::instance()->addSensors();
    return HW_OK;
}

HW_INT Controller::Device_ServiceCommandReceiveHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_CHAR *pcDevId;
    HW_CHAR *pcReqId;
    HW_CHAR *pcServiceId;
    HW_CHAR *pcMethod;
    HW_BYTES *pbstrContent;

    pcDevId = HW_MsgGetStr(pstMsg,EN_IOTA_DATATRANS_IE_DEVICEID);
    pcReqId = HW_MsgGetStr(pstMsg,EN_IOTA_DATATRANS_IE_REQUESTID);
    pcServiceId = HW_MsgGetStr(pstMsg,EN_IOTA_DATATRANS_IE_SERVICEID);
    pcMethod = HW_MsgGetStr(pstMsg,EN_IOTA_DATATRANS_IE_METHOD);
    pbstrContent = HW_MsgGetBstr(pstMsg,EN_IOTA_DATATRANS_IE_CMDCONTENT);

    HW_LOG_INF((HW_CHAR*)" -------------- CommandReceiveHandler -------------- DeviceId=%s", pcDevId);

    if ((HW_NULL == pcDevId) ||(HW_NULL == pcReqId) ||(HW_NULL == pcServiceId) ||(HW_NULL == pcMethod))
    {
        HW_LOG_ERR((HW_CHAR*)"RcvCmd is invalid, pcDevId=%s, pcReqId=%s, pcServiceId=%s, pcMethod=%s.",
                   pcDevId, pcReqId, pcServiceId, pcMethod);
        return HW_ERR;
    }

    std::string channel , data;
    channel = Controller::instance()->cfgs_.get_string("server_data_mq");
    IotMessageDeviceCommand command;
    command.device_id = Application::instance()->getConfig().get_string("device_id");
//    command.device_id = pcDevId;
    std::string sensor_device_id ;
    sensor_device_id = Controller::instance()->get_device_id( pcDevId);

    std::vector<std::string> fields;
    boost::split(fields, sensor_device_id, boost::is_any_of(("-")));
//    command.sensor_type = boost::lexical_cast<int>(fields[1]);
//    command.sensor_id = boost::lexical_cast<int>(fields[2]);
    command.service_id = pcServiceId;
    command.method = pcMethod;
    command.content.assign(pbstrContent->pcByte,pbstrContent->uiLen) ;
    // sensor_type and sensor_type be included in 'content'

    data = command.marshall();
    Controller::instance()->redis_->publish(channel,data );

//    if (0 == strncmp(METHOD_REMOVE_GATEWAY,pcMethod,strlen(METHOD_REMOVE_GATEWAY)))
//    {
//        IOTA_RmvGateWay();
//    }

    return HW_OK;
}

HW_INT Controller::Device_ServiceDataReportResultHandler(HW_UINT uiCookie, HW_MSG pstMsg) {
    HW_UINT uiResult;

    uiResult = HW_MsgGetUint (pstMsg, EN_IOTA_DATATRANS_IE_RESULT,HW_FAILED);
    if (HW_SUCCESS != uiResult) {
        HW_LOG_ERR((HW_CHAR*)" ---------------- DataReport failed -------------- uiResult=%u.",uiResult);
        return HW_ERR;
    }

    HW_LOG_INF((HW_CHAR*)" -------------- DataReport success --------------");
    return HW_OK;
}

// 添加 端设备
// 从端设备文件中读取 /var/data/xxx/sensors.txt
HW_VOID Controller::addSensors(){
    ST_IOTA_DEVICE_INFO  stDeviceInfo = {0};
    Config sensors;
    std::string value;
    Config runtime;

    runtime = iot_load_runtime_config();

    sensors = iot_load_device_config();
    int num ;
    num = sensors.get_int("sensor_num");

    sensor_id_with_cookie_.clear();
    // 一次读出多个端设备信息进行注册
    for(int n=1;n<= num ;n++){
        std::uint32_t cookie;

        cookie = HW_GeneralCookie();

        std::memset( &stDeviceInfo , 0 , sizeof(stDeviceInfo));
        value = sensors.get_string("sensor_"+ boost::lexical_cast<std::string>(n) + ".NodeId");

        sensor_id_with_cookie_[cookie] = value;

        if( runtime.get_string(value) != ""){
            iot_device_status_update(value,"ONLINE","NONE");
            iot_device_data_report(value,"Switch","{\"value\":1}");
            continue;
        }

        stDeviceInfo.pcNodeId = (HW_CHAR*) value.c_str();
        value = sensors.get_string("sensor_"+ boost::lexical_cast<std::string>(n) + ".ManufacturerName");
        stDeviceInfo.pcManufacturerName = (HW_CHAR*) value.c_str();
        value = sensors.get_string("sensor_"+ boost::lexical_cast<std::string>(n) + ".ManufacturerId");
        stDeviceInfo.pcManufacturerId =  (HW_CHAR*) value.c_str();
        value = sensors.get_string("sensor_"+ boost::lexical_cast<std::string>(n) + ".DeviceType");
        stDeviceInfo.pcDeviceType = (HW_CHAR*) value.c_str();
        value = sensors.get_string("sensor_"+ boost::lexical_cast<std::string>(n) + ".Model");
        stDeviceInfo.pcModel = (HW_CHAR*) value.c_str();
        value = sensors.get_string("sensor_"+ boost::lexical_cast<std::string>(n) + ".ProtocolType");
        stDeviceInfo.pcProtocolType = (HW_CHAR*) value.c_str();

        value = sensors.get_string("sensor_"+ boost::lexical_cast<std::string>(n) + ".Name");
        stDeviceInfo.pcName = (HW_CHAR*) value.c_str();


        IOTA_HubDeviceAdd( cookie, &stDeviceInfo);
    }

}

//端设备添加回调
HW_INT Controller::Device_AddResultHandler(HW_UINT uiCookie, HW_MSG pstMsg) {
    HW_UINT uiResult;
    uiResult = HW_MsgGetUint(pstMsg, EN_IOTA_HUB_IE_RESULT,0);

    Config runtime;
    runtime = Controller::instance()->iot_load_runtime_config();

//    printf("%d\n",uiResult);
    if (EN_IOTA_HUB_RESULT_SUCCESS != uiResult) {
        HW_LOG_ERR((HW_CHAR *)" -------------- AddDevice failed --------------- uiResult=%u.",uiResult);
        if( uiResult == EN_IOTA_HUB_RESULT_DEVICE_EXIST){
            HW_LOG_ERR((HW_CHAR*)"Error: DEVICE_EXIST");

        }
        return HW_ERR;
    }

    std::string iot_device_id = HW_MsgGetStr(pstMsg, EN_IOTA_HUB_IE_DEVICEID);
    std::string device_id = Controller::instance()->sensor_id_with_cookie_[uiCookie];
    runtime.set_string(device_id,iot_device_id);
    runtime.set_string(iot_device_id, device_id);

    Controller::instance()->iot_save_runtime_config(runtime);
    Controller::instance()->device_id_with_iot_id_[device_id] = iot_device_id;


//    HW_LOG_INF(" -------------- AddDeviceAck --------------- DeviceID=%s.",g_cDeviceId);
    IOTA_DeviceStatusUpdate( HW_GeneralCookie(), (HW_CHAR*)iot_device_id.c_str(), (HW_CHAR*)"ONLINE", (HW_CHAR*)"NONE");

    HW_Sleep(5);
//    Sensor_DataReport();

//    HW_Sleep(30);
//    if(HW_NULL != g_cDeviceId)
//        IOTA_HubDeviceRemove(g_uiCookie, g_cDeviceId);

    return HW_OK;
}

HW_INT Controller::Device_DevUpDateHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_UINT uiResult;
    HW_CHAR *pcDeviceId;

    uiResult = HW_MsgGetUint (pstMsg, EN_IOTA_HUB_IE_RESULT,0);
    pcDeviceId = HW_MsgGetStr (pstMsg, EN_IOTA_HUB_IE_DEVICEID);

    if (EN_IOTA_HUB_RESULT_SUCCESS != uiResult)
    {
        HW_LOG_ERR((HW_CHAR*)"------------- Update Device failed --------------- uiResult=%u,DevId=%s.", uiResult, pcDeviceId);
        return HW_ERR;
    }

    HW_LOG_INF((HW_CHAR*)"------------- Update Device success ---------------- DeviceId=%s.", pcDeviceId);
    return HW_OK;
}


HW_INT Controller::Device_RemovResultHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_UINT uiResult;

    uiResult = HW_MsgGetUint (pstMsg, EN_IOTA_HUB_IE_RESULT,0);
    if (EN_IOTA_HUB_RESULT_SUCCESS != uiResult)
    {
        HW_LOG_ERR((HW_CHAR*)" -------------- Remov Device failed ---------------- uiResult=%u.", uiResult);
        return HW_ERR;
    }

    HW_LOG_INF((HW_CHAR*)" ------------- Remove Device success ----------------");
    return HW_OK;
}

HW_INT Controller::Device_DisconnectHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_UINT uiReason;

    //stop reporting data
    Controller::instance()->iot_logined_ = false;

    uiReason = HW_MsgGetUint(pstMsg, EN_IOTA_LGN_IE_REASON, EN_IOTA_LGN_REASON_NULL);
    HW_LOG_INF((HW_CHAR*)" --------------- Disconnected(reson=%u) ----------------!", uiReason);
    if (EN_IOTA_LGN_REASON_DEVICE_RMVED == uiReason || EN_IOTA_LGN_REASON_DEVICE_NOEXIST == uiReason) {
        Controller::instance()->iot_reset_runtime_config();
    }

    if ( EN_IOTA_LGN_REASON_NULL != uiReason){
        HW_Sleep(5);
        Controller::instance()->iot_start();
    }

    return HW_OK;
}


HW_INT Controller::Gateway_UnbindRecvtHandler(HW_UINT uiCookie, HW_MSG pstMsg) {
    Controller::instance()->iot_logined_ = false;
    HW_LOG_INF((HW_CHAR*)"------------- UnbindRecvtHandler ----------%s---------!", pstMsg);
    return HW_OK;
}