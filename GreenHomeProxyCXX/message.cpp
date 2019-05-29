#include "message.h"
#include <jsoncpp/json/json.h>

 
typedef std::function< std::shared_ptr<Message> (const Json::Value& root) > ParseFunc;

std::vector<ParseFunc> parse_func_list={
		IotMessageDeviceOnline::parse,
		IotMessageDeviceOffline::parse,
		IotMessageSensorDeviceOnline::parse,
		IotMessageSensorDeviceOffline::parse,
		IotMessageSensorDeviceStatusReport::parse,
		IotMessageDeviceCommand::parse,
		IotMessageHeartbeat::parse

};

Message::Ptr MessageJsonParser::parse(const char * data,size_t size){
	Json::Reader reader;
	Json::Value root;
	Message::Ptr msg;
	if (reader.parse(data, root)){
		for(auto func:parse_func_list){
			msg = func(root);
			if(msg){
				msg->id_ = root["id"].asString();
				
				
				break;
			}
		}
	}
	return msg;
}


std::shared_ptr<Message> IotMessageHeartbeat::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() == IOT_MESSAGE_HEARTBEAT){
		std::shared_ptr<IotMessageHeartbeat> msg = std::make_shared<IotMessageHeartbeat>();
		msg->unmarshall(root);
		result = msg ;
	}
	return result;
}

Json::Value IotMessageHeartbeat::values(){
	return Message::values();
}


std::shared_ptr<Message> IotMessageDeviceOnline::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() ==  IOT_MESSAGE_DEVICE_ONLINE){
		std::shared_ptr<IotMessageDeviceOnline> msg = std::make_shared<IotMessageDeviceOnline>();
		msg->unmarshall(root);
		result = msg ;
	}
	return result;
}


std::shared_ptr<Message> IotMessageDeviceOffline::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() ==  IOT_MESSAGE_DEVICE_OFFLINE){
		std::shared_ptr<IotMessageDeviceOffline> msg = std::make_shared<IotMessageDeviceOffline>();
		msg->unmarshall(root);
		result = msg ;
	}
	return result;
}

std::shared_ptr<Message> IotMessageSensorDeviceOnline::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() ==  IOT_MESSAGE_SENSOR_DEVICE_ONLINE){
		std::shared_ptr<IotMessageSensorDeviceOnline> msg = std::make_shared<IotMessageSensorDeviceOnline>();
		msg->unmarshall(root);
		Json::Value values = root["values"];
		msg->sensor_id = values["sensor_id"].asInt();
		msg->sensor_type = values["sensor_type"].asInt();
		result = msg ;
	}
	return result;
}

Json::Value IotMessageSensorDeviceOnline::values(){
	Json::Value values = Message::values();
	values["sensor_id"] = sensor_id;
	values["sensor_type"] = sensor_type;
	return values;
}

std::shared_ptr<Message> IotMessageSensorDeviceOffline::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() ==  IOT_MESSAGE_SENSOR_DEVICE_OFFLINE){
		std::shared_ptr<IotMessageSensorDeviceOffline> msg = std::make_shared<IotMessageSensorDeviceOffline>();
		msg->unmarshall(root);
		Json::Value values = root["values"];
		msg->sensor_id = values["sensor_id"].asInt();
		msg->sensor_type = values["sensor_type"].asInt();
		result = msg ;
	}
	return result;
}

Json::Value IotMessageSensorDeviceOffline::values(){
	Json::Value values = Message::values();
	values["sensor_id"] = sensor_id;
	values["sensor_type"] = sensor_type;
	return values;
}

std::shared_ptr<Message> IotMessageSensorDeviceStatusReport::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() ==  IOT_MESSAGE_SENSOR_DEVICE_STATUS_REPORT){
		std::shared_ptr<IotMessageSensorDeviceStatusReport> msg = std::make_shared<IotMessageSensorDeviceStatusReport>();

		Json::Value values = root["values"];
		msg->sensor_id = values["sensor_id"].asInt();
		msg->sensor_type = values["sensor_type"].asInt();
		msg->service_id = values["service_id"].asString();
		msg->status_data = values["status_data"].asString();
		msg->unmarshall(root);
		result = msg ;
	}
	return result;
}

Json::Value IotMessageSensorDeviceStatusReport::values(){
	Json::Value values = Message::values();
	values["sensor_id"] = sensor_id;
	values["sensor_type"] = sensor_type;
	values["service_id"] = service_id;
	values["status_data"] = status_data;
	return values;
}


std::shared_ptr<Message> IotMessageDeviceCommand::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() ==  IOT_MESSAGE_DEVICE_COMMAND){
		std::shared_ptr<IotMessageDeviceCommand> msg = std::make_shared<IotMessageDeviceCommand>();
		msg->unmarshall(root);
		Json::Value values = root["values"];
		msg->sensor_id = values["sensor_id"].asInt();
		msg->sensor_type = values["sensor_type"].asInt();
		msg->service_id = values["service_id"].asString();
		msg->method = values["method"].asString();
		msg->content = values["content"].asString();

		result = msg ;
	}
	return result;
}

Json::Value IotMessageDeviceCommand::values(){
	Json::Value values = Message::values();
	values["sensor_id"] = sensor_id;
	values["sensor_type"] = sensor_type;
	values["service_id"] = service_id;
	values["method"] = method;
	values["content"] = content;
	return values;
}

/*
 *
 *
 * http://open-source-parsers.github.io/jsoncpp-docs/doxygen/index.html
 *
 */



