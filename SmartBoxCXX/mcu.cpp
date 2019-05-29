#include "mcu.h"

#include <fstream>
#include <ostream>
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>

#ifdef  BOOST_OS_LINUX
#include <sys/ioctl.h>
#endif

#include "message.h"
#include "Controller.h"
#include "utils.h"
#include "app.h"


//McuController::McuController(boost::asio::io_service& io_service):io_service_(io_service){
//
//}

boost::asio::io_service& McuController::io_service(){
	return *Controller::instance()->io_service();
}

bool McuController::init(const Config & cfgs){
//	sec_cfgs_file_  = "seczone.txt";
	cfgs_ = cfgs;
	init_configs();
//	load_configs(sec_cfgs_file_);	// 从文件中覆盖
//	load_configs("seczone.user");	// 读取用户配置数据

	PropertyStringMap sensor_props;
	sensor_props["port"] = cfgs.get_string("seczone_serial_port");
	sensor_props["baudrate"] = cfgs.get_string("seczone_serial_baudrate");
	sensor_.init(sensor_props);
	sensor_.setListener(this);

	heartbeat_interval_ = cfgs.get_int("sensor_hb_interval",5);
	max_offline_time_ = cfgs.get_int("sensor_offline_time",3600); // 默认1小时收不到心跳包
	last_heartbeat_time = std::time(NULL);
	return true;
}

bool McuController::open(){
	sensor_.open();

	running_ = true;
	timer_ = std::make_shared<boost::asio::steady_timer>(io_service());
	timer_->expires_after(std::chrono::seconds( heartbeat_interval_));
	timer_->async_wait(std::bind(&McuController::check_heartbeat, this));

//	std::thread thread(std::bind(&McuController::get_gpio_status,this));
//	std::thread thread(&McuController::get_gpio_status,this);
	return true;
}

//离线通知 innercontroller 是否要重启设备
void McuController::onSensorOffline(){
	Controller::instance()->reboot();
}

// 定时发送 心跳包到 sensor
// 检查 单片机 sensor 是否心跳超时
void McuController::check_heartbeat(){
	if( !running_ ){
		return;
	}

	if( std::time(NULL) - last_heartbeat_time > max_offline_time_ ){
		onSensorOffline();
	}

	last_heartbeat_time = std::time(NULL);

	timer_->expires_after(std::chrono::seconds( heartbeat_interval_));
	timer_->async_wait(std::bind(&McuController::check_heartbeat, this));
}

void McuController::close(){
	running_ = false;
}


void McuController::hearbeat(){
	std::shared_ptr< SensorMessageHeartbeat > message = std::make_shared<SensorMessageHeartbeat>();
	sensor_.sendMessage(message);
}

bool McuController::setPassword(const std::string& old,const std::string& _new ){

	save_configs();
	return true;
}

//停
//保存防区信息 （写入用户配置文件)
void McuController::save_configs() {

}

bool McuController::load_configs(const std::string& seczone_file){

	return true;
}

//生成默认的防区参数
void McuController::init_configs(){


//	save_configs();
}



//接收到上行的防区设备消息
void McuController::onMessage(std::shared_ptr<MessagePayload> &message, Sensor *sensor) {
	{
		if(message->a ==(int) MessageType::Heartbeat){
			last_heartbeat_time = std::time(NULL);
			return;
		}
	}

	// 处理报警信息
	//接收传感器上报消息
	if(message->a == (int)MessageType::SensorStatusValue){
		std::shared_ptr<MessageSensorStatus> m = std::make_shared<MessageSensorStatus>();
		m->sensor_id = message->c;
		m->sensor_type = message->b;
		std::string name,value;
		name = message->d ;
		value = message->e;
		m->params[name] = value;
		Controller::instance()->onTraverseUpMessage(m);

		setFeatureValue(message);
	}

	if(message->a == (int)MessageType::McuStatusValue){
		std::shared_ptr<MessageDeviceStatus> m = std::make_shared<MessageDeviceStatus>();
		std::string name,value;
		name = message->d ;
		value = message->e;
		m->params[name] = value;
		Controller::instance()->onTraverseUpMessage(m);

//		setFeatureValue(message);
	}
}

// 发送端点控制消息
bool McuController::sendMessage(const MessagePayload::Ptr payload){
	sensor_.sendMessage(payload);
	return true;
}

// 缓存最新的设备状态值
void McuController::setFeatureValue(const MessagePayload::Ptr message){
	std::string uid;
	uid = message->uniqueId();
	feature_values_[uid] = message;
}

//查询当前端点设备某一项功能的状态值
std::string McuController::getFeatureValue(const SensorDeviceFeatureUniqueId& feature_id){
	std::string value;
	if( feature_values_.find(feature_id) != feature_values_.end() ){
		auto p = feature_values_[ feature_id ];
		value = p->e;
	}
	return value;
}

std::string McuController::getFeatureValue(const std::string& b, const std::string& c, const std::string& d){
	SensorDeviceFeatureUniqueId uid;
	uid = b+"."+c+"_"+ d;
	return getFeatureValue(uid);
}

// 设置端点设备的参数值（包括控制)
bool McuController::setSensorValue(const std::string& sensor_id, const std::string& sensor_type ,
					const std::string& name , const std::string& value ){
    if(name == "test"){
        // todo . for test
        // 模拟上报sensor状态值
        return true;
    }
	std::shared_ptr< MessagePayload> p = std::make_shared<MessagePayload>();
	p->a = (int)MessageType::SensorValueSet;
	p->b = (int) boost::lexical_cast<int >(sensor_type);
	p->c = (int) boost::lexical_cast<int>(sensor_id);
	p->d = name;
	p->e = value;
	this->sendMessage(p);
	return true;
}

// 获取端点设备的所有当前运行状态值
PropertyStringMap McuController::getSensorStatus(const std::string& sensor_id,
								  const std::string& sensor_type){
	PropertyStringMap values;
	std::string prex = sensor_type + "." + sensor_id;
	for(auto p : feature_values_){
		std::string feature_name;
		std::string feature_value;

		std::vector<std::string> fields;
		boost::split(fields, p.first, boost::is_any_of(("_")));
		if(fields.size() == 2){
			if( fields[0] == prex){
				feature_name = fields[1];
				feature_value = p.second->e;
				values[feature_name] = feature_value;
			}
		}
	}

	// 再做一次查询
	std::shared_ptr< MessagePayload> p = std::make_shared<MessagePayload>();
	p->a = (int)MessageType::SensorStatusQuery;
	p->b = (int) boost::lexical_cast<int >(sensor_type);
	p->c = (int) boost::lexical_cast<int>(sensor_id);
	this->sendMessage(p);

	return values;
}
