//
// Created by bin zhang on 2019/1/11.
//

#ifndef INNERPROC_INNERCONTROLLER_H
#define INNERPROC_INNERCONTROLLER_H

#include "base.h"
#include "service.h"
#include "iot.h"

#include <jsoncpp/json/json.h>
#include <sw/redis++/redis++.h>
using namespace sw::redis;


class Controller:  public std::enable_shared_from_this<Controller> {

public:
	typedef std::shared_ptr<Controller> Ptr;
	bool init(const Config& props);
	bool open();
	void close();
	void run();
	
	static std::shared_ptr<Controller>& instance(){
		static std::shared_ptr<Controller> handle ;
		if(!handle.get()){
			handle = std::make_shared<Controller>() ;
		}
		return handle;
	}

	Json::Value getStatusInfo();

	bool initRedis();

	bool initIotHub();
protected:
	void recvFromRedis();
	void iot_register_broadcast();
	bool iot_bind_gateway();
	static HW_INT iot_RegResultHandler(HW_UINT uiCookie, HW_MSG pstMsg);
	static HW_INT Device_ConnectedHandler(HW_UINT uiCookie, HW_MSG pstMsg);
	static HW_INT Device_ServiceCommandReceiveHandler(HW_UINT uiCookie, HW_MSG pstMsg);
	static HW_INT Device_ServiceDataReportResultHandler(HW_UINT uiCookie, HW_MSG pstMsg); // 状态上报回报
	static HW_INT Device_AddResultHandler(HW_UINT uiCookie, HW_MSG pstMsg) ;
	static HW_INT Device_DevUpDateHandler(HW_UINT uiCookie, HW_MSG pstMsg);
	static HW_INT Device_RemovResultHandler(HW_UINT uiCookie, HW_MSG pstMsg);
	static HW_INT Device_DisconnectHandler(HW_UINT uiCookie, HW_MSG pstMsg);
	static HW_INT Gateway_UnbindRecvtHandler(HW_UINT uiCookie, HW_MSG pstMsg);
//    static HW_INT Device_ServiceCommandReceiveHandler(HW_UINT uiCookie, HW_MSG pstMsg);

	HW_VOID addSensors(); // 添加所有下挂设备
	bool iot_start();
	bool iot_init();
	Config iot_load_device_config();
    Config iot_load_runtime_config();
    void iot_reset_runtime_config();
	void iot_save_runtime_config(Config & runtime);
	std::string get_iot_device_id(const std::string& device_id);
	std::string get_device_id(const std::string& iot_id);
	std::string get_device_id(const std::string& sensor_type, const std::string& sensor_id);
	bool iot_login();
	bool iot_device_status_update(const std::string& device_id, const std::string& status , const std::string& detail) ;

	bool iot_device_data_report(const std::string& device_id, const std::string& service_id, const std::string& jsondata);

	void processAppMessage(const std::string& data);
protected:
	Config 		cfgs_;
	std::thread * readThread_;
	Redis  * redis_;
	bool iot_logined_ ;
	std::atomic_bool running_;
	bool iot_bind_ok_;

	std::map< std::uint32_t , std::string > sensor_id_with_cookie_;
	std::map< std::string , std::string > device_id_with_iot_id_;
};


#endif //INNERPROC_INNERCONTROLLER_H
