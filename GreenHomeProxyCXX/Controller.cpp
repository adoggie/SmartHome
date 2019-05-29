//
// Created by bin zhang on 2019/1/11.
//

#include "Controller.h"
#include "include/iota_device.h"
#include "include/hw_json.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "examples/demo.h"
#include "app.h"
#include "message.h"

bool Controller::init(const Config& props){
	cfgs_ = props;
	running_ = false;
    ConnectionOptions connection_options;
    Config & cfg = Application::instance()->getConfig();

    connection_options.host = cfg.get_string("redis.host","127.0.0.1");
    connection_options.port = cfg.get_int("redis.port",6379); 			// The default port is 6379.
//	connection_options.password = "auth";   // Optional. No password by default.
    connection_options.db = cfg.get_int("redis.db",0);
    connection_options.socket_timeout = std::chrono::milliseconds(200);

// Connect to Redis server with a single connection.
    redis_ = new Redis(connection_options);
//    redis_->publish(pubname, json_text);

	readThread_ = new std::thread(std::bind(&Controller::recvFromRedis,this));
    iot_init();
	iot_start();
    return true;
}


void Controller::processAppMessage(const std::string& data){
	Application::instance()->getLogger().debug("Message Recved : " + data);
	Message::Ptr message = MessageJsonParser::parse(data.c_str(),data.length());
	if( !message){
		Application::instance()->getLogger().error("Message Data Parse Error:" + data);
		return ;
	}
	{
		std::shared_ptr<IotMessageDeviceOnline> m = std::dynamic_pointer_cast<IotMessageDeviceOnline>(message);
		if(m){
			iot_device_status_update(cfgs_.get_string("device_id"),"ONLINE","NONE");
		}
	}

	{
		std::shared_ptr<IotMessageDeviceOffline> m = std::dynamic_pointer_cast<IotMessageDeviceOffline>(message);
		if(m){
			iot_device_status_update(cfgs_.get_string("device_id"),"OFFLINE","NONE");
		}
	}

//		{
//			std::shared_ptr<IotMessageSensorDeviceOnline> m = std::dynamic_pointer_cast<IotMessageSensorDeviceOnline>(message);
//			if(m){
//				std::string device_id;
//				device_id = get_device_id( boost::lexical_cast<std::string>(m->sensor_type) ,
//				        boost::lexical_cast<std::string>(m->sensor_id));
//				iot_device_status_update(device_id,"ONLINE","NONE");
//			}
//		}
//
//		{
//			std::shared_ptr<IotMessageSensorDeviceOffline> m = std::dynamic_pointer_cast<IotMessageSensorDeviceOffline>(message);
//			if(m){
//				std::string device_id;
//				device_id = get_device_id( boost::lexical_cast<std::string>(m->sensor_type) ,
//										   boost::lexical_cast<std::string>(m->sensor_id));
//				iot_device_status_update(device_id,"OFFLINE","NONE");
//			}
//		}

	{
		std::shared_ptr<IotMessageSensorDeviceStatusReport> m = std::dynamic_pointer_cast<IotMessageSensorDeviceStatusReport>(message);
		if(m){
			std::string device_id;
//				device_id = get_device_id( boost::lexical_cast<std::string>(m->sensor_type) ,
//										   boost::lexical_cast<std::string>(m->sensor_id));
			device_id = cfgs_.get_string("device_id");
			iot_device_data_report(device_id,m->service_id,m->status_data);
		}
	}
}

void Controller::recvFromRedis(){

	auto sub = redis_->subscriber();
	auto this_ = this;
// Set callback functions.
	sub.on_message([this](std::string channel, std::string data) {
		// Process message of MESSAGE type.
		try {
			processAppMessage(data);
		}catch (const std::exception& e){
			Application::instance()->getLogger().error(e.what());
		}catch(...){}



	});

	std::string device_id ;
	device_id = cfgs_.get_string("device_id");
	sub.subscribe(device_id);
	//	sub.psubscribe("pattern1*");
    running_ = true;
// Consume messages in a loop.
	while ( running_ ) {
		try {
			sub.consume();
		}catch (const TimeoutError &e) {
			continue;
		} catch (const Error &err) {
			// Handle exceptions.
		}
	}
	Application::instance()->getLogger().info("Redis Subscribe Thread Exited.");
}

bool Controller::open(){
	if(cfgs_.get_bool("smartbox.watchdog.enable")) {
//		watchdog_.open();
	}
	
	if(cfgs_.get_bool("smartbox.seczone.enable")) {
//		seczone_guard_.open();
	}
	return true;
}


bool Controller::initRedis(){
	return false;
}

bool Controller::initIotHub(){
	return true;
}

void Controller::close(){
//	watchdog_.close();
//	seczone_guard_.close();
//	HttpService::instance()->close();
}

void Controller::run(){

	readThread_->join();
}


Json::Value Controller::getStatusInfo(){
	return Json::Value();
}