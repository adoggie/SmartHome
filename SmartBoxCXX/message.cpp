#include "message.h"
#include <jsoncpp/json/json.h>
#include "sensor.h"

 
typedef std::function< std::shared_ptr<Message> (const Json::Value& root) > ParseFunc;

std::vector<ParseFunc> parse_func_list={
//		MessageLogin::parse,
		MessageLoginResp::parse,
		MessageHeartBeat::parse,
		MessageDeviceStatusQuery::parse,
//		MessageDeviceStatus::parse,
		MessageDeviceValueSet::parse,
		MessageSensorStatusQuery::parse,
//		MessageSensorStatus::parse,
		MessageSensorValueSet::parse,

		MessageAppJoinRequest::parse

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


std::shared_ptr<Message> MessageLoginResp::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() ==  MESSAGE_LOGIN_RESP){
		std::shared_ptr<MessageLoginResp> msg = std::make_shared<MessageLoginResp>();
		Json::Value values = root["values"];
		msg->error = values["error"].asInt();
		msg->message =  values["message"].asString();
		msg->server_time = values["server_time"].asUInt();
		msg->unmarshall(values);
		result = msg ;
	}
	return result;
}

std::shared_ptr<Message> MessageDeviceStatusQuery::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() ==  MESSAGE_STATUS_QUERY){
		std::shared_ptr<MessageDeviceStatusQuery> msg = std::make_shared<MessageDeviceStatusQuery>();
		Json::Value values = root["values"];
		msg->MessageTraverse::unmarshall(values);
		result = msg ;
	}
	return std::shared_ptr<MessageDeviceStatusQuery>();
}

std::shared_ptr<MessagePayload> MessageDeviceStatusQuery::asPayload() const{
	std::shared_ptr<MessagePayload> p = std::make_shared<MessagePayload>();
	p->a = (int)MessageType::McuStatusQuery;

	return p;
}

std::shared_ptr<MessagePayload> MessageSensorStatusQuery::asPayload() const{
	std::shared_ptr<MessagePayload> p = std::make_shared<MessagePayload>();
	p->a = (int)MessageType::SensorStatusQuery;
	p->b = sensor_type;
	p->c = sensor_id;
	return p;
}


std::shared_ptr<MessagePayload> MessageSensorValueSet::asPayload() const{
	std::shared_ptr<MessagePayload> p = std::make_shared<MessagePayload>();
	p->a = (int)MessageType::SensorValueSet;
	p->b = sensor_type;
	p->c = sensor_id;
	p->d = param_name;
	p->e = param_value;
	return p;
}

std::shared_ptr<Message> MessageSensorValueSet::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() == MESSAGE_SENSOR_VALUE_SET){
		auto msg = std::make_shared<MessageSensorValueSet>();
		Json::Value values = root["values"];
		msg->sensor_type = values["sensor_type"].asInt();
		msg->sensor_id = values["sensor_id"].asInt();
		msg->param_name = values["param_name"].asString();
		msg->param_value = values["param_value"].asString();
		msg->unmarshall(values);
		result = msg;
	}
	return result;
}

std::shared_ptr<MessagePayload> MessageDeviceValueSet::asPayload() const{
	std::shared_ptr<MessagePayload> p = std::make_shared<MessagePayload>();
	p->a = (int)MessageType::McuValueSet;
	p->b = boost::lexical_cast<int>(mod_type);
	p->d = param_name;
	p->e = param_value;
	return p;
}


std::shared_ptr<Message> MessageHeartBeat::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() == "heartbeat"){
		std::shared_ptr<MessageHeartBeat> msg = std::make_shared<MessageHeartBeat>();
		Json::Value values = root["values"];
		msg->unmarshall(values);
		result = msg;
	}
	return result;
}

std::shared_ptr<Message> MessageDeviceValueSet::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() == MESSAGE_VALUE_SET){
		auto msg = std::make_shared<MessageDeviceValueSet>();
		Json::Value values = root["values"];
		msg->mod_type = values["mod_type"].asString();
		msg->param_name = values["param_name"].asString();
		msg->param_value = values["param_value"].asString();
		msg->unmarshall(values);
		result = msg;
	}
	return result;
}

// 端点设备状态查询请求
std::shared_ptr<Message> MessageSensorStatusQuery::parse(const Json::Value& root){
	std::shared_ptr<Message> result;
	if( root["name"].asString() == MESSAGE_SENSOR_STATUS_QUERY){
		auto msg = std::make_shared<MessageSensorStatusQuery>();
		Json::Value values = root["values"];
		msg->sensor_type = values["sensor_type"].asInt();
		msg->sensor_id = values["sensor_id"].asInt();
		msg->unmarshall(values);
		result = msg;
	}
	return result;
}


//=================

std::shared_ptr<Message> MessageAppJoinRequest::parse(const Json::Value& root){
    std::shared_ptr<Message> result;
    if( root["name"].asString() ==  MESSAGE_APP_JOIN_REQUEST){
        std::shared_ptr<MessageAppJoinRequest> msg = std::make_shared<MessageAppJoinRequest>();
        Json::Value values = root["values"];
        msg->token = values["token"].asString();
        msg->id =  values["id"].asString();
        msg->type = values["type"].asString();
        result = msg ;
    }
    return result;
}


Json::Value MessageAppJoinReject::values(){
    Json::Value node;
    node["reason"] = reason;
    return node;
}

Json::Value MessageAppJoinAccept::values(){
    Json::Value vs;
    return vs ;
}


/*
 *
 *
 * http://open-source-parsers.github.io/jsoncpp-docs/doxygen/index.html
 *
 */



