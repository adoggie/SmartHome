//
// Created by bin zhang on 2019/1/10.
//

#ifndef SMARTBOX_TCP_CHANNEL_H
#define SMARTBOX_TCP_CHANNEL_H

#include <memory>

#include  "base.h"
#include "message.h"
#include "service.h"
#include "server.h"

// TcpCommandChannel
// 支持手机app连接注册，并从box推送设备消息到手机app

class TcpCommandChannelManager:Service,IConnectionListener { // ,std::enable_shared_from_this<InnerConnectionManager>{

public:
	static std::shared_ptr<TcpCommandChannelManager>& instance(){
		static std::shared_ptr<TcpCommandChannelManager> handle ;
		if(!handle.get()){
			handle = std::make_shared<TcpCommandChannelManager>() ;
		}
		return handle;
	}
	
	bool  init(const Config& cfgs);
	
	bool open();
	void close();
	
	void onJoinRequest(const std::shared_ptr<MessageAppJoinRequest> & msg,const Connection::Ptr& conn);
	void onConnected(const Connection::Ptr & conn);
	void onDisconnected(const Connection::Ptr & conn);
	void onJsonText(const std::string & text,const Connection::Ptr& conn);

	void postMessage(const std::shared_ptr<Message> & message); // 发送消息到所有连接app
	bool isBusy();
protected:
	std::shared_ptr<SocketServer>   sockserver_;
//	std::vector< Connection::Ptr>  app_conns_; //  进入的多个app连接对象

	std::map<std::string,Connection::Ptr> conn_ids_;
	std::shared_ptr<SocketServer>    server_;
//	boost::asio::io_service io_service_;
};




#endif //INNERPROC_INNER_DEVICE_MGR_H
