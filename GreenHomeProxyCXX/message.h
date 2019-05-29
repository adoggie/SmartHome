//
// Created by bin zhang on 2019/1/6.
//

#ifndef INNERPROC_MESSAGE_H
#define INNERPROC_MESSAGE_H

#include "base.h"
#include <jsoncpp/json/json.h>

//struct Message{
//	typedef std::shared_ptr<Message> Ptr;
//};
//typedef std::list< std::shared_ptr<Message> > MessageList_t;
//

#define IOT_MESSAGE_DEVICE_ONLINE "device_online"
#define IOT_MESSAGE_DEVICE_OFFLINE "device_offline"
#define IOT_MESSAGE_SENSOR_DEVICE_ONLINE "sensor_device_offline"
#define IOT_MESSAGE_SENSOR_DEVICE_OFFLINE "sensor_device_offline"
#define IOT_MESSAGE_SENSOR_DEVICE_STATUS_REPORT "sensor_device_status_report" // 设备状态上报
#define IOT_MESSAGE_DEVICE_COMMAND "device_command"  // 设备控制命令
#define IOT_MESSAGE_HEARTBEAT "heartbeat"  // 设备控制命令



class MessageJsonParser;

class Message {
protected:
	std::string id_;
	std::string name_;
	PropertyMap values_;
public:
	std::string device_id;

	friend class MessageJsonParser;
public:
	Message(){}
	Message(const std::string & name):name_(name){}
	virtual ~Message(){}
public:
	typedef std::shared_ptr<Message> Ptr;
	
	boost::any value(const std::string& name,boost::any def_=boost::any())  {
		try {
			return values_.at(name);
		}catch (...){
		
		}
		return def_;
	}
	
	std::string getValueString(const std::string&name , const std::string& def_=""){
		try {
			return boost::any_cast<std::string>(this->value(name));
//		}catch (boost::bad_any_cast)
		}catch(...){
			return def_;
		}
	}
	
	std::string& name() { return name_;}
//	virtual bool serialize(Json::Value& root){
//		root["id"] = id_;
//
//		return true;
//	}
	virtual Json::Value values(){
        Json::Value values;
        values["device_id"] = device_id;
	    return values;
	}
	
	virtual  std::string marshall(){
		Json::Value root;
		Json::Value arrayObj;
		Json::Value item;
		root["id"] = id_;
		root["name"] = name_;
		Json::Value values = this->values();
		if( !values.isNull()){
		    values["device_id"] = device_id;
			root["values"] = values;
		}
		return root.toStyledString();
	}
	virtual bool unmarshall(const Json::Value& root){
	    Json::Value values = root["values"];
	    device_id = values["device_id"].asString();
	    return true;
	}
};


struct IotMessageHeartbeat:Message{
    IotMessageHeartbeat():Message(IOT_MESSAGE_HEARTBEAT){
    }

    static std::shared_ptr<Message> parse(const Json::Value& root);
    virtual Json::Value values();

};

struct IotMessageDeviceOnline:Message{
	IotMessageDeviceOnline():Message(IOT_MESSAGE_DEVICE_ONLINE){
	}
	
	static std::shared_ptr<Message> parse(const Json::Value& root);
//	Json::Value values();
	
};

struct IotMessageDeviceOffline:Message{
//	std::string reason;
	IotMessageDeviceOffline():Message(IOT_MESSAGE_DEVICE_OFFLINE){
	}
	
	static std::shared_ptr<Message> parse(const Json::Value& root);
//	Json::Value values();
};

struct IotMessageSensorDeviceOnline:Message{
	int sensor_type;
	int sensor_id;
	IotMessageSensorDeviceOnline():Message(IOT_MESSAGE_SENSOR_DEVICE_ONLINE){
	    sensor_id = 0;
	    sensor_type = 0;
	}
	
	static std::shared_ptr<Message> parse(const Json::Value& root);
	virtual Json::Value values();
};

struct IotMessageSensorDeviceOffline:Message{
    int sensor_type;
    int sensor_id;
	IotMessageSensorDeviceOffline():Message(IOT_MESSAGE_SENSOR_DEVICE_OFFLINE){
        sensor_id = 0;
        sensor_type = 0;
	}

	static std::shared_ptr<Message> parse(const Json::Value& root);
	virtual Json::Value values();
};


struct IotMessageSensorDeviceStatusReport:Message{
    int sensor_type;
    int sensor_id;
    std::string service_id;
    std::string status_data;
	IotMessageSensorDeviceStatusReport():Message(IOT_MESSAGE_SENSOR_DEVICE_STATUS_REPORT){
        sensor_id = 0;
        sensor_type = 0;
	}

	static std::shared_ptr<Message> parse(const Json::Value& root);
	virtual Json::Value values();
};

struct IotMessageDeviceCommand:Message{
	int sensor_type;
    int sensor_id;
    std::string service_id;
    std::string method;
    std::string content;
	IotMessageDeviceCommand():Message(IOT_MESSAGE_DEVICE_COMMAND){
        sensor_id = 0;
        sensor_type = 0;
	}

	static std::shared_ptr<Message> parse(const Json::Value& root);
	virtual  Json::Value values();
};

class MessageJsonParser{
public:
	static Message::Ptr parse(const char * data,size_t size);
	
};






#endif //INNERPROC_MESSAGE_H
