#include "demo.h"
#include "../include/iota_device.h"
#include "../include/hw_json.h"
#include "stdio.h"
#include "stdlib.h"
#include "string.h"

ST_GATEWAY_INFO g_stGateWayInfo={0};

HW_UINT g_uiLoginFlg = HW_FALSE;
HW_UINT g_uiLogLevel = 0;
HW_UINT g_uiCookie= 1;
HW_CHAR *g_cDeviceId = HW_NULL;
HW_INT _main()
{

    HW_CHAR acBuf[BUFF_MAX_LEN];
    IOTA_Init(CONFIG_PATH, HW_NULL);
    HW_LOG_INF("---------------- IOTA_Init ------------------");
    DEVICE_InitGateWayInfo();
    DEVICE_ReadConf();

	registerBroadcast();

    if (HW_NULL == g_stGateWayInfo.pcDeviceID)
    {
        while(1)
        {
            if(HW_OK == DEVICE_BindGateWay())
            {   
                HW_LOG_INF("---------------- IOTA_Register ok ----------------");
                break;
            }
            
            HW_Sleep(1);
            continue;
        }
    }
    else
    {
        IOTA_ConfigSetStr(EN_IOTA_CFG_DEVICEID, g_stGateWayInfo.pcDeviceID);  
        IOTA_ConfigSetStr(EN_IOTA_CFG_IOCM_ADDR, g_stGateWayInfo.pcIOCMAddr);
        IOTA_ConfigSetStr(EN_IOTA_CFG_APPID, g_stGateWayInfo.pcAppID);
        IOTA_ConfigSetStr(EN_IOTA_CFG_DEVICESECRET, g_stGateWayInfo.pcSecret);          
        IOTA_ConfigSetStr(EN_IOTA_CFG_MQTT_ADDR, g_stGateWayInfo.pcIOCMAddr);
        IOTA_ConfigSetUint(EN_IOTA_CFG_MQTT_PORT, g_stGateWayInfo.pcMqttPort);
        IOTA_ConfigSetUint(EN_IOTA_CFG_IOCM_PORT, g_stGateWayInfo.pcIOCMPort);
        
        HW_LogSetLevel(g_uiLogLevel);
        IOTA_Login();
        HW_LOG_INF("---------------- IOTA_Login -----------------");
        sprintf(acBuf, "%s/%s", IOTA_TOPIC_SERVICE_COMMAND_RECEIVE, g_stGateWayInfo.pcDeviceID);
        HW_BroadCastReg(acBuf, Device_ServiceCommandReceiveHandler);   
		HW_LOG_INF("--------------- Reg CommandReceiveHandler ----------------- acBuf=%s", acBuf);

        sprintf(acBuf, "%s/%s", IOTA_TOPIC_DATATRANS_REPORT_RSP, g_stGateWayInfo.pcDeviceID);
        HW_BroadCastReg(acBuf, Device_ServiceDataReportResultHandler);
		HW_LOG_INF("--------------- Reg DataReportResultHandler ----------------- acBuf=%s", acBuf);
    }   
    
    // 延时时间长一点，防止还在做添加删除操作时，IOTA_Logout()已经执行了
    HW_Sleep(100);
    IOTA_Logout();
    HW_LOG_INF("--------------- IOTA_Logout ---------------");
    HW_Sleep(5);
    IOTA_Destroy();
    HW_LOG_INF("--------------- IOTA_Destroy -----------------");
    
    
    while (1)
    {
        HW_Sleep(10000);
    }
    return HW_OK;
    
}

HW_VOID registerBroadcast()
{
	HW_BroadCastReg(IOTA_TOPIC_BIND_RSP, Device_RegResultHandler);
	HW_BroadCastReg(IOTA_TOPIC_CMD_UNBIND_RECEIVE, Gateway_UnbindRecvtHandler);
	HW_BroadCastReg(IOTA_TOPIC_CONNECTED_NTY, Device_ConnectedHandler);
	HW_BroadCastReg(IOTA_TOPIC_DISCONNECT_NTY, Device_DisconnectHandler);
	HW_BroadCastReg(IOTA_TOPIC_HUB_ADDDEV_RSP, Device_AddResultHandler);
	HW_BroadCastReg(IOTA_TOPIC_HUB_RMVDEV_RSP, Device_RemovResultHandler);
	HW_BroadCastReg(IOTA_TOPIC_DEVUPDATE_RSP, Device_DevUpDateHandler);
}

HW_VOID DEVICE_InitGateWayInfo()
{
    
    if (HW_NULL != g_stGateWayInfo.pcDeviceID)
    {
        free(g_stGateWayInfo.pcDeviceID);
        g_stGateWayInfo.pcDeviceID = HW_NULL;
    }

    if (HW_NULL != g_stGateWayInfo.pcName)
    {
        free(g_stGateWayInfo.pcName);
        g_stGateWayInfo.pcName = HW_NULL;
    }
    
    if (HW_NULL != g_stGateWayInfo.pcSecret)
    {
        free(g_stGateWayInfo.pcSecret);
        g_stGateWayInfo.pcSecret = HW_NULL;
    }
    
    if (HW_NULL != g_stGateWayInfo.pcIOCMAddr)
    {
        free(g_stGateWayInfo.pcIOCMAddr);
        g_stGateWayInfo.pcIOCMAddr = HW_NULL;
    }
    
    if (HW_NULL != g_stGateWayInfo.pcAppID)
    {
        free(g_stGateWayInfo.pcAppID);
        g_stGateWayInfo.pcAppID = HW_NULL;
    }
    
    if (HW_NULL != g_stGateWayInfo.pcIODMAddr)
    {
        free(g_stGateWayInfo.pcIODMAddr);
        g_stGateWayInfo.pcIODMAddr = HW_NULL;
    }

    return;
}
HW_VOID DEVICE_ReadConf()
{        
    FILE* fp = HW_NULL;
    char acName[BUFF_MAX_LEN]; 
    int file_size; 
    HW_CHAR *pcJsonStr;
    HW_JSONOBJ jsonObj;
    HW_JSON json;
    HW_CHAR *pcDeviceID;    
    HW_CHAR *pcSecret;    
    HW_CHAR *pcAppID;    
    HW_CHAR *pcIOCMAddr;   
    HW_CHAR *pcIODMAddr;
    HW_UINT uiLen;
    
    //get gw reg info
    sprintf(acName, "%s/%s", CONFIG_PATH, GATEWAY_BIND_INFO_FILE);
    
    fp = fopen(acName, "r"); 
  
    if (fp == HW_NULL)
    {
        HW_LOG_INF("IOTA_ReadConf():open file(%s) failed.\n", acName);
        return;
    }
        
    fseek(fp, 0, SEEK_END); 
    file_size = ftell(fp); 
    pcJsonStr = (char *)malloc((file_size+1) * sizeof( char ) ); 
    
    if (HW_NULL == pcJsonStr)
    {
        fclose(fp);
        return;
    }
    
    fseek(fp, 0, SEEK_SET);  
    fread(pcJsonStr, file_size, sizeof(char), fp);    
    pcJsonStr[file_size] = '\0'; 
    fclose(fp); 

    jsonObj = HW_JsonDecodeCreate(pcJsonStr, HW_TRUE);
    json = HW_JsonGetJson(jsonObj);

    pcDeviceID = HW_JsonGetStr(json, IOTA_CFG_DEVICEID);
    if (HW_NULL != pcDeviceID)
    {
        uiLen = strlen(pcDeviceID);
        g_stGateWayInfo.pcDeviceID = malloc(uiLen+1);
        strcpy(g_stGateWayInfo.pcDeviceID, pcDeviceID); 
        g_stGateWayInfo.pcDeviceID[uiLen] = '\0';
    }
    
    pcSecret = HW_JsonGetStr(json, IOTA_CFG_DEVICESECRET);    
    if (HW_NULL != pcSecret)
    {
        uiLen = strlen(pcSecret);
        g_stGateWayInfo.pcSecret = malloc(uiLen+1);
        strcpy(g_stGateWayInfo.pcSecret, pcSecret); 
        g_stGateWayInfo.pcSecret[uiLen] = '\0';
    }
    
    pcIOCMAddr = HW_JsonGetStr(json, IOTA_CFG_IOCM_ADDR);    
    if (HW_NULL != pcIOCMAddr)
    {
        uiLen = strlen(pcIOCMAddr);
        g_stGateWayInfo.pcIOCMAddr = malloc(uiLen+1);
        strcpy(g_stGateWayInfo.pcIOCMAddr, pcIOCMAddr); 
        g_stGateWayInfo.pcIOCMAddr[uiLen] = '\0';
    }

    pcAppID = HW_JsonGetStr(json, IOTA_CFG_APPID);   
    if (HW_NULL != pcAppID)
    {
        uiLen = strlen(pcAppID);
        g_stGateWayInfo.pcAppID = malloc(uiLen+1);
        strcpy(g_stGateWayInfo.pcAppID, pcAppID); 
        g_stGateWayInfo.pcAppID[uiLen] = '\0';
    }

    pcIODMAddr = HW_JsonGetStr(json, IOTA_CFG_IODM_ADDR);    
    if (HW_NULL != pcIODMAddr)
    {
        uiLen = strlen(pcIODMAddr);
        g_stGateWayInfo.pcIODMAddr = malloc(uiLen+1);
        strcpy(g_stGateWayInfo.pcIODMAddr, pcIODMAddr); 
        g_stGateWayInfo.pcIODMAddr[uiLen] = '\0';
    }

    g_stGateWayInfo.pcIOCMPort = HW_JsonGetUint(json, IOTA_CFG_IOCM_PORT, 0);
    g_stGateWayInfo.pcMqttPort = HW_JsonGetUint(json, IOTA_CFG_MQTT_PORT, 0);
    g_uiLogLevel = HW_JsonGetUint(json, IOTA_LOGLEVEL,0);
    
    HW_JsonObjDelete(&jsonObj);
    free(pcJsonStr);      
    return;
}

HW_UINT DEVICE_BindGateWay()
{    
    ST_IOTA_DEVICE_INFO  stDeviceInfo = {0};
    FILE *fp = HW_NULL;
    FILE *fpEsn = HW_NULL;
    HW_CHAR szGwRegInfoFileName[BUFF_MAX_LEN] = {0};
    HW_CHAR linebuf[BUFF_MAX_LEN] = {0};
    HW_UINT uiLen = 0;
    HW_UINT uiLoop = 0;
    HW_UINT uiCnt = 0;
    //HW_CHAR szEsnInfo[BUFF_MAX_LEN] = {0};
    HW_UINT uiPort = 0;
    int file_size; 
    HW_CHAR *pcJsonStr;
    HW_JSONOBJ jsonObj;
    HW_JSON json;
    HW_CHAR *pucEsnFile;
    HW_CHAR *pucPlatformAddr;

    //get gw reg info
    sprintf(szGwRegInfoFileName, "%s/%s", CONFIG_PATH, GATEWAY_REG_INFO_FILE);
    fp = fopen(szGwRegInfoFileName, "r");
    if (HW_NULL == fp)
    {
        HW_LOG_ERR("open %s fail.\r\n", szGwRegInfoFileName);
        return HW_ERR;
    }
    
    fseek(fp , 0, SEEK_END); 
    file_size = ftell(fp); 
    pcJsonStr = (char *)malloc( (file_size+1) * sizeof( char ) ); 
    
    if (HW_NULL == pcJsonStr)
    {
        fclose(fp);
        return HW_ERR;
    }
    
    fseek(fp, 0, SEEK_SET);  
    fread(pcJsonStr, file_size, sizeof(char), fp);    
    pcJsonStr[file_size ] = '\0'; 
    fclose(fp); 

    jsonObj = HW_JsonDecodeCreate(pcJsonStr, HW_TRUE);
    json = HW_JsonGetJson(jsonObj);
	
    pucPlatformAddr = HW_JsonGetStr(json, IOTA_PLATFORM_ADDR);
    uiPort = HW_JsonGetUint(json, IOTA_PLATFORM_PORT,8943);
	stDeviceInfo.pcMac = HW_JsonGetStr(json, IOTA_DEVICE_MAC);
	stDeviceInfo.pcNodeId = stDeviceInfo.pcMac;
    stDeviceInfo.pcManufacturerId = HW_JsonGetStr(json, IOTA_MANUFACTURE_ID);
    stDeviceInfo.pcDeviceType = HW_JsonGetStr(json, IOTA_DEVICE_TYPE);
    stDeviceInfo.pcModel = HW_JsonGetStr(json, IOTA_MODEL);
    stDeviceInfo.pcProtocolType = HW_JsonGetStr(json, IOTA_PROTOCOL_TYPE);
    g_uiLogLevel = HW_JsonGetUint(json, IOTA_LOGLEVEL,0);
    HW_LogSetLevel(g_uiLogLevel); 

    if(0 == strlen(pucPlatformAddr))
    {
        HW_LOG_ERR("get platform ip fail.\r\n");
        HW_JsonObjDelete(&jsonObj);
        free(pcJsonStr);   
        return HW_ERR;
    }

    IOTA_ConfigSetStr(EN_IOTA_CFG_IOCM_ADDR, pucPlatformAddr);   
    IOTA_ConfigSetUint(EN_IOTA_CFG_IOCM_PORT, uiPort);      
    IOTA_Bind(stDeviceInfo.pcMac, &stDeviceInfo);
 

    HW_JsonObjDelete(&jsonObj);
    free(pcJsonStr);   
    return HW_OK;
}

HW_INT Device_RegResultHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_CHAR *pcDeviceId;
    HW_CHAR *pcDeviceSecret;
    HW_CHAR *pcAppId;
    HW_CHAR *pcIoCMServerAddr;
    
    HW_UINT pcIoCMServerport;
    HW_UINT pcMQTTServerport;
    HW_CHAR *pcMQTTServerAddr;
    
    
    HW_CHAR acBuf[BUFF_MAX_LEN];
    HW_UINT uiRegRet;    
    HW_JSONOBJ hJsonObj;     
    HW_JSON rootjson;
    HW_CHAR *pcJsonStr;
    FILE* fw = HW_NULL;
    char aszName[BUFF_MAX_LEN];

    uiRegRet = HW_MsgGetUint(pstMsg, EN_IOTA_BIND_IE_RESULT, EN_IOTA_BIND_RESULT_FAILED);
    if (EN_IOTA_BIND_RESULT_SUCCESS != uiRegRet)
    {
        HW_LOG_ERR("---------------- Reg failed ------------------ Result=%u.", uiRegRet);
        return HW_ERR;
    }   
    
    HW_LOG_INF("--------------- Reg success -----------------");
    
    pcDeviceId = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_DEVICEID);
    pcDeviceSecret = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_DEVICESECRET);
    pcAppId = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_APPID);
    pcIoCMServerAddr = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_IOCM_ADDR);
    pcMQTTServerAddr = HW_MsgGetStr(pstMsg, EN_IOTA_BIND_IE_MQTT_ADDR);
    pcIoCMServerport = HW_MsgGetUint(pstMsg, EN_IOTA_BIND_IE_IOCM_PORT,8943);
    pcMQTTServerport = HW_MsgGetUint(pstMsg, EN_IOTA_BIND_IE_MQTT_PORT,8883);
    hJsonObj = HW_JsonObjCreate();
    rootjson = HW_JsonGetJson(hJsonObj);

	HW_LOG_INF("--------------- Reg success ----------------- gatewayId=%s" , pcDeviceId);

    HW_JsonAddStr(rootjson, IOTA_CFG_DEVICEID, pcDeviceId);
    HW_JsonAddStr(rootjson, IOTA_CFG_DEVICESECRET, pcDeviceSecret);
    HW_JsonAddStr(rootjson, IOTA_CFG_APPID, pcAppId);
    HW_JsonAddStr(rootjson, IOTA_CFG_IOCM_ADDR, pcIoCMServerAddr);
    
    HW_JsonAddUint(rootjson, IOTA_CFG_IOCM_PORT, pcIoCMServerport);
    HW_JsonAddUint(rootjson, IOTA_CFG_MQTT_PORT, pcMQTTServerport);
    HW_JsonAddStr(rootjson, IOTA_CFG_MQTT_ADDR, pcMQTTServerAddr);
    
    HW_JsonAddUint(rootjson, IOTA_LOGLEVEL, g_uiLogLevel);    
    pcJsonStr = HW_JsonEncodeStr(hJsonObj);

    sprintf(aszName, "%s/%s", CONFIG_PATH, GATEWAY_BIND_INFO_FILE);
    fw = fopen(aszName, "w");
    if (fw == HW_NULL)
    {
        HW_JsonObjDelete(&hJsonObj);
        HW_LOG_ERR("Open(%s) failed.",aszName);
        return HW_ERR;
    }    
    
    fputs(pcJsonStr, fw);
    fclose(fw);
    HW_JsonObjDelete(&hJsonObj);   

    DEVICE_ReadConf();
    sprintf(acBuf, "%s/%s", IOTA_TOPIC_SERVICE_COMMAND_RECEIVE, g_stGateWayInfo.pcDeviceID);
    HW_BroadCastReg(acBuf, Device_ServiceCommandReceiveHandler);
	HW_LOG_INF("--------------- Reg CommandReceiveHandler ----------------- acBuf=%s", acBuf);

    sprintf(acBuf, "%s/%s", IOTA_TOPIC_DATATRANS_REPORT_RSP, g_stGateWayInfo.pcDeviceID);
    HW_BroadCastReg(acBuf, Device_ServiceDataReportResultHandler); 
	HW_LOG_INF("--------------- Reg DataReportResultHandler ----------------- acBuf=%s", acBuf);

    IOTA_Login();

    return HW_OK;
}


HW_INT Gateway_UnbindRecvtHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    g_stGateWayInfo.uiLoginFlg = HW_FALSE;
    IOTA_RmvGateWay();
	HW_LOG_INF("------------- UnbindRecvtHandler ----------%s---------!", pstMsg);
    return HW_OK;
}

HW_INT Device_ConnectedHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_CHAR *pcJsonStr;

    HW_LOG_INF("--------------- ConnectedHandler gateway connected ----------------!");

    g_uiLoginFlg = HW_TRUE;

	Gateway_DataReport(&pcJsonStr);    
    
    HW_Sleep(5);
    AddSensors();
    g_uiCookie ++;
    return HW_OK;    
}


HW_VOID AddSensors()
{
    ST_IOTA_DEVICE_INFO  stDeviceInfo = {0};
    FILE *fp = NULL;
    HW_CHAR szdeviceInfoFileName[BUFF_MAX_LEN] = {0};
    HW_INT  file_size; 
    HW_CHAR *pcJsonStr;
    HW_JSONOBJ jsonObj;
    HW_JSON json;

    //IOTA_HubDeviceRemove(g_uiCookie, "xxxx-xxxx-xxxx"); //deviceId can be obtained from portal or local database.

    //get device info   
	stDeviceInfo.pcNodeId = "SN Number_8532157";
	stDeviceInfo.pcManufacturerName = "Huawei";
	stDeviceInfo.pcManufacturerId = "Huawei";
	stDeviceInfo.pcDeviceType = "Motion";
	stDeviceInfo.pcModel = "test01";
	stDeviceInfo.pcProtocolType = "Z-Wave";

    IOTA_HubDeviceAdd(g_uiCookie, &stDeviceInfo);
    return;   
}


HW_INT Device_DisconnectHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_UINT uiReason;
    
    //stop reporting data
    g_uiLoginFlg = HW_FALSE;     
    
    uiReason = HW_MsgGetUint(pstMsg, EN_IOTA_LGN_IE_REASON, EN_IOTA_LGN_REASON_NULL); 
    HW_LOG_INF(" --------------- Disconnected(reson=%u) ----------------!", uiReason);
    if (EN_IOTA_LGN_REASON_DEVICE_RMVED == uiReason)
    {        
        IOTA_RmvGateWay();       
    }
    
    return HW_OK;
}

HW_INT Device_AddResultHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_UINT uiResult;
    
    
    uiResult = HW_MsgGetUint(pstMsg, EN_IOTA_HUB_IE_RESULT,0);
    printf("%d\n",uiResult);
    if (EN_IOTA_HUB_RESULT_SUCCESS != uiResult)
    {
        HW_LOG_ERR(" -------------- AddDevice failed --------------- uiResult=%u.",uiResult); 
        return HW_ERR;
    }

    g_cDeviceId = HW_MsgGetStr(pstMsg, EN_IOTA_HUB_IE_DEVICEID); 
    HW_LOG_INF(" -------------- AddDeviceAck --------------- DeviceID=%s.",g_cDeviceId);
    IOTA_DeviceStatusUpdate(g_uiCookie, g_cDeviceId, "ONLINE", "NONE");

    HW_Sleep(5);
	Sensor_DataReport();
    
    HW_Sleep(30);
    if(HW_NULL != g_cDeviceId)
      IOTA_HubDeviceRemove(g_uiCookie, g_cDeviceId);
    
    return HW_OK;
}

HW_VOID Sensor_DataReport()
{
	Device_ServiceDataReport(g_cDeviceId, "Battery", "{\"batteryLevel\":98}");
	Device_ServiceDataReport(g_cDeviceId, "Motion", "{\"motion\":\"DETECTED\"}");
}

HW_VOID Gateway_DataReport(HW_CHAR **pcJsonStr)
{
	HW_JSON json;
	HW_JSONOBJ hJsonObj;

	hJsonObj = HW_JsonObjCreate();
	json = HW_JsonGetJson(hJsonObj);
	HW_JsonAddUint(json, (HW_CHAR*)"storage", (HW_INT)10240); 
	HW_JsonAddUint(json, (HW_CHAR*)"usedPercent", (HW_INT)20); 
	*pcJsonStr = HW_JsonEncodeStr(hJsonObj);
	Device_ServiceDataReport(g_stGateWayInfo.pcDeviceID, "Storage", *pcJsonStr);
	//another method
	//Device_ServiceDataReport(pcDeviceId, "Storage", "{\"storage\":20240,\"usedPercent\":20}");
}

HW_INT Device_RemovResultHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_UINT uiResult;
    
    uiResult = HW_MsgGetUint (pstMsg, EN_IOTA_HUB_IE_RESULT,0);
    if (EN_IOTA_HUB_RESULT_SUCCESS != uiResult)
    {
        HW_LOG_ERR(" -------------- Remov Device failed ---------------- uiResult=%u.", uiResult); 
        return HW_ERR;
    }
   
    HW_LOG_INF(" ------------- Remove Device success ----------------");
    return HW_OK;
}

HW_INT Device_DevUpDateHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_UINT uiResult;
    HW_CHAR *pcDeviceId;
    
    uiResult = HW_MsgGetUint (pstMsg, EN_IOTA_HUB_IE_RESULT,0);
    pcDeviceId = HW_MsgGetStr (pstMsg, EN_IOTA_HUB_IE_DEVICEID);
    
    if (EN_IOTA_HUB_RESULT_SUCCESS != uiResult)
    {
        HW_LOG_ERR("------------- Update Device failed --------------- uiResult=%u,DevId=%s.", uiResult, pcDeviceId); 
        return HW_ERR;
    }

    HW_LOG_INF("------------- Update Device success ---------------- DeviceId=%s.", pcDeviceId);
    return HW_OK;
}

HW_INT Device_ServiceDataReportResultHandler(HW_UINT uiCookie, HW_MSG pstMsg)
{
    HW_UINT uiResult;
        
    uiResult = HW_MsgGetUint (pstMsg, EN_IOTA_DATATRANS_IE_RESULT,HW_FAILED);
    if (HW_SUCCESS != uiResult)
    {
        HW_LOG_ERR(" ---------------- DataReport failed -------------- uiResult=%u.",uiResult); 
        //TODO handle deivce report failed result
        return HW_ERR;
    }

    HW_LOG_INF(" -------------- DataReport success --------------");
    return HW_OK;
}
HW_INT Device_ServiceCommandReceiveHandler(HW_UINT uiCookie, HW_MSG pstMsg)
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
    
	HW_LOG_INF(" -------------- CommandReceiveHandler -------------- DeviceId=%s", pcDevId);

    if ((HW_NULL == pcDevId) ||(HW_NULL == pcReqId) ||(HW_NULL == pcServiceId) ||(HW_NULL == pcMethod))
    {
        HW_LOG_ERR("RcvCmd is invalid, pcDevId=%s, pcReqId=%s, pcServiceId=%s, pcMethod=%s.",
                    pcDevId, pcReqId, pcServiceId, pcMethod); 
        return HW_ERR;
    }

    if (0 == strncmp(METHOD_REMOVE_GATEWAY,pcMethod,strlen(METHOD_REMOVE_GATEWAY)))
    {
        IOTA_RmvGateWay();
    }
   
    return HW_OK;
}

HW_VOID IOTA_RmvGateWay()
{
    char acName[BUFF_MAX_LEN] = {0};    
    FILE* fp = HW_NULL;
    
    sprintf(acName, "%s/%s", CONFIG_PATH, GATEWAY_BIND_INFO_FILE);  
    
    fp = fopen(acName, "r");     
    if (HW_NULL != fp)
    {
        fclose(fp);
        remove(acName);
        HW_LOG_INF("-------------- IOTA_RmvGateWay --------------- remove bindfile=%s",acName);
    }    

    return;
}

HW_INT Device_ServiceDataReport(HW_CHAR *pcSensorDeviceID, HW_CHAR *pcServiceId, HW_CHAR *pcServiceProperties)
{    
    HW_CHAR aszRequestId[BUFF_MAX_LEN];
    
    HW_GetRequestId(aszRequestId);

    if (HW_TRUE != g_uiLoginFlg)
    {
        //TODO e.g. resend service data
        HW_LOG_INF("Device_MApiMsgRcvHandler():GW discon,pcJsonStr=%s", pcServiceProperties);
        return HW_ERR;
    }

	HW_LOG_INF("-------------- ServiceDataReport --------------- requestId=%s, deviceId=%s", aszRequestId, pcSensorDeviceID);

    IOTA_ServiceDataReport(HW_GeneralCookie(), aszRequestId, pcSensorDeviceID, pcServiceId, pcServiceProperties);
    return HW_OK;
}
HW_UINT HW_GeneralCookie()
{
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

