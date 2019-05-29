//
// Created by bin zhang on 2019/1/10.
//
#include <mutex>

#include "tcpchannel.h"
#include "app.h"

#include "Controller.h"

#define SCOPE_LOCK std::lock_guard<std::recursive_mutex> lock(rmutex_);

bool  TcpCommandChannelManager::init(const Config& cfgs){
	cfgs_ = cfgs;
	std::string ip;
	unsigned  short port;
	ip = cfgs.get_string("listen_ip","127.0.0.1");
	port = (unsigned short) cfgs.get_int("listen_port",7892);

	ip = Controller::instance()->getInnerIP();
	server_ = std::make_shared<SocketServer>(* Controller::instance()->io_service(),ip,port);
	return true ;
}

bool TcpCommandChannelManager::open(){
	server_->setListener(this);
	server_->start();
	
	std::string ip;
	unsigned  short port;
	ip = cfgs_.get_string("listen_ip","127.0.0.1");
	port = (unsigned short) cfgs_.get_int("listen_port",7892);
	ip = Controller::instance()->getInnerIP();

	Application::instance()->getLogger().info( (boost::format("TcpCommandChannelManager started.. serving on:%d,%s")%port%ip).str() );
	
	return true;
}

void TcpCommandChannelManager::close(){
	server_->close();
}

// APP 连接进入
void TcpCommandChannelManager::onConnected(const Connection::Ptr & conn){
	// 居然卡住了
	SCOPE_LOCK
	conn_ids_[conn->id()] = conn;
    Application::instance()->getLogger().debug("App Socket Established!");
}

// 室内设备断开连接
void TcpCommandChannelManager::onDisconnected(const Connection::Ptr & conn){
	SCOPE_LOCK
	Application::instance()->getLogger().debug("App Socket Lost!");
	{
		auto itr = conn_ids_.find(conn->id());
		if (itr != conn_ids_.end()) {
			conn_ids_.erase(itr);
		}
	}
}

void TcpCommandChannelManager::onJsonText(const std::string & text,const Connection::Ptr& conn){
	//
	SCOPE_LOCK
	Application::instance()->getLogger().debug("App Message Recieved:" + text);
	Message::Ptr message = MessageJsonParser::parse(text.c_str(),text.length());
	if(!message){
		return ;
	}

	{//	请求加入家庭
		std::shared_ptr<MessageAppJoinRequest> msg = std::dynamic_pointer_cast<MessageAppJoinRequest>(message);
		if(msg) {
//			onJoinFamily(msg,conn); // 设备加入家庭
		}
	}


}

void TcpCommandChannelManager::onJoinRequest(const std::shared_ptr<MessageAppJoinRequest>& msg,const Connection::Ptr & conn){
	// verify msg->token
	// todo.  校验token有效性

	// 缓存设备对象，并发送同意加入消息
//	InnerDevice::Ptr device = std::make_shared<InnerDevice>(conn);
//	device->device_id = msg->id;
//	device->device_type = msg->type;
//	device->token = msg->token;
//	device_ids_[conn->id()] = device; // 加入设备列表
//
//	conn->send(MessageJoinAccept().marshall());
}

bool TcpCommandChannelManager::isBusy(){

	return false;
}

// 发送消息到所有连接app
void TcpCommandChannelManager::postMessage(const std::shared_ptr<Message> & message){
    std::string text;
    text = message->marshall();
    Application::instance()->getLogger().debug("Post Message :" + text);

    for(auto itr: conn_ids_){
        itr.second->send( text );
    }
}


