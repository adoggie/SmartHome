//
// Created by bin zhang on 2019/2/5.
//
/**
 * mcu.h
 * 记录接入控制设备sensor的所有状态值，供本地网络中的设备查询
 * 提供本地网络设备的直接对sensor的控制
 */
#ifndef INNERPROC_SECZONE_H
#define INNERPROC_SECZONE_H

#include "base.h"
#include <stdio.h>
#include <time.h>
#include <thread>
#include <jsoncpp/json/json.h>
#include <boost/asio.hpp>

#include "config.h"
#include "message.h"
#include "sensor.h"
//#include "event.h"
#include "McuChannel.h"


//struct SensorDeviceUniqueId{
//	std::string type;
//	std::string id;
//};
typedef std::string SensorDeviceFeatureUniqueId;
typedef std::string SensorDeviceUniqueId; // sensor_type.sensor_id
typedef std::string FeatureName;
typedef std::string FeatureValue;

typedef std::map< FeatureName , FeatureValue > FeatureItemMap;
// 设备当前最新的状态值
typedef std::map< SensorDeviceFeatureUniqueId, MessagePayload::Ptr > SensorFeatureValues;
typedef std::map< SensorDeviceUniqueId, FeatureItemMap> SensorFeatures;

class McuController:public ISensorListener{
public:
    typedef std::shared_ptr<McuController> Ptr;
    static std::shared_ptr<McuController>& instance(){
        static std::shared_ptr<McuController> handle ;
        if(!handle.get()){
            handle = std::make_shared<McuController>() ;
        }
        return handle;
    }
    McuController(){}

//	McuController( boost::asio::io_service& io_service);
	bool init(const Config & cfgs);
	bool open();
	void close();
	bool setPassword(const std::string& old,const std::string& _new );
    boost::asio::io_service& io_service();
	void onMessage(std::shared_ptr<MessagePayload> &payload, Sensor *sensor) ; // 接收到上行消息

	void hearbeat();    //
	void setFeatureValue(const MessagePayload::Ptr payload);
	std::string getFeatureValue(const SensorDeviceUniqueId& sensor , const std::string& feature_name);
	std::string getFeatureValue(const std::string& b, const std::string& c, const std::string& d);

	bool sendMessage(const MessagePayload::Ptr payload); //向设备发送消息

	bool setSensorValue(const std::string& sensor_id, const std::string& sensor_type ,
						const std::string& name , const std::string& value ); 	// 设置端点设备的参数值（包括控制)
	PropertyStringMap getSensorStatus(const std::string& sensor_id,
									  const std::string& sensor_type); // 获取端点设备的所有当前运行状态值
	SensorFeatures getAllSensorFeatures();
private:

	void init_configs();
	bool load_configs(const std::string& seczone_file);

	void save_configs();

	void check_heartbeat();
	void onSensorOffline();	// 传感器离线


//	SensorFeatureValues featureValues();
//	void emergencyDetected(const std::shared_ptr< Event_Emergency> & event); //报警触发
private:
//	std::vector<seczone_mode_info_t> sec_modes_;
	std::recursive_mutex mutex_;
	Config sec_cfgs_;
	Config cfgs_;
	std::string sec_cfgs_file_;
//	seczone_settings_t seczone_settings_;
	Sensor 	sensor_;
	std::shared_ptr<boost::asio::steady_timer> 	timer_;
//	boost::asio::io_service & io_service_;

	int heartbeat_interval_;
	int max_offline_time_;			// sensor 模块最大检测离线时间
	std::time_t  last_heartbeat_time;

	std::atomic_bool running_;

	std::string     rand_key_;  //控制开门的密码
    std::time_t     last_rand_key_time_;    // 最新生成randkey的时间
//	SensorFeatureValues	feature_values_;
	SensorFeatures  sensor_features_;
    McuChannel   mcu_tcp_channel_;
};
#endif //INNERPROC_SECZONE_H
