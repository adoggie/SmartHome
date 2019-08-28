//
// Created by scott on 2019-06-07.
//

#include "McuChannel.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "app.h"
#include "version.h"
#include "base64_.h"
#include "Controller.h"
#include "mcu.h"

#define SP '\n'
//#define SPS "\n"


bool McuChannel::init(const Config& props){

    cfgs_ = props;

    check_timer_interval_ = cfgs_.get_int("controller.check_timer",5);

    timer_ = std::make_shared<boost::asio::steady_timer>( *Controller::instance()->io_service());
    timer_->expires_after(std::chrono::seconds( check_timer_interval_));
    timer_->async_wait(std::bind(&McuChannel::workTimedTask, this));

    return true;
}

bool McuChannel::open(){

    mcu_channel_port_ = cfgs_.get_int("mcu_channel_port",8001);
    mcu_channel_host_ = cfgs_.get_string("mcu_channel_host","127.0.0.1");

//	reportEvent( std::make_shared<Event_SystemStart>());
    if(TEST){ // for test
//    if(1){ // for test
//        std::string text = "322C31332C302C302C302C30D467\n";
//        std::string text = "322C31332C302C302C312C30E357\n";
        std::string text = "302C312C322C332C342C35F517\n";
//        onRecv(text.c_str(),text.size());
        onJsonText(text,Connection::Ptr());
        MessagePayload p;
        p.marshall();
    }

    return true;
}


void McuChannel::close(){

}


// 定时工作任务
void McuChannel::workTimedTask(){
    std::lock_guard<std::recursive_mutex> lock(rmutex_);


    if(!conn_ ){
        // 准备发起连接到mcu host
        conn_ = std::make_shared<Connection>( *Controller::instance()->io_service());
        conn_->setListener(this);
        conn_->setSP('\n');
        boost::asio::ip::address address = boost::asio::ip::make_address( mcu_channel_host_ );
        boost::asio::ip::tcp::endpoint ep(address,(std::uint32_t ) mcu_channel_port_);
        std::stringstream ss;
        ss<<"Connect to Mcu Channel Host:" << mcu_channel_host_ << ":" << mcu_channel_port_;
        Application::instance()->getLogger().debug(ss.str());
        conn_->startConnect(ep);
        last_heart_time_ = std::time(NULL);
    }

    // 如果超时接收不到来自服务器的心跳包，则关闭连接，再次进行登录
    int interval = cfgs_.get_int("mcu_channel_heartbeat",1000);
    if( std::time(NULL) - last_heart_time_ > interval*1){
        resetStatus();
//		last_check_time_ = std::time(NULL);
//		check_net_reachable();
    }

    if(conn_){
        //发送心跳
//        MessageHeartBeat hb;
//        hb.device_id = getDeviceUniqueID();
//        conn_->send(hb.marshall());
    }

    timer_->expires_after(std::chrono::seconds( check_timer_interval_));
    timer_->async_wait(std::bind(&McuChannel::workTimedTask, this));
}


//void McuChannel::check_net_reachable() {
//}

//请求所有sensor上报一次
void McuChannel::reqUpdateSensorStatus(){
    MessageSensorStatusQuery msg;
    msg.sensor_type = 0;
    msg.sensor_id = 0 ;  // 所有sensors 上报状态
    auto payload = msg.asPayload();
    McuController::instance()->sendMessage(payload);

}

void McuChannel::onConnected(const Connection::Ptr& conn){
    std::lock_guard<std::recursive_mutex> lock(this->rmutex_);

    std::shared_ptr<MessageLogin> login_req = std::make_shared<MessageLogin> ();

    Application::instance()->getLogger().debug("Mcu Channel Host Proxy Connected.");

    reqUpdateSensorStatus();
//	live_time_outside_ = std::time(NULL);
}

//外部连接丢失
void McuChannel::onDisconnected(const Connection::Ptr& conn){
    std::lock_guard<std::recursive_mutex> lock(this->rmutex_);
    Application::instance()->getLogger().debug("Connection Disconnected..");
    resetStatus();

//	live_time_inside_ = live_time_outside_ = 0;
}

void McuChannel::onData( boost::asio::streambuf& buffer,const Connection::Ptr& conn){

}

void McuChannel::resetStatus(){
    std::lock_guard<std::recursive_mutex> lock(rmutex_);

    if(conn_){
        conn_->close();
        conn_.reset();
    }
}

//对外连接失败
void McuChannel::onConnectError(const Connection::Ptr& conn,ConnectionError error){
    std::lock_guard<std::recursive_mutex> lock(this->rmutex_);
    Application::instance()->getLogger().error("Connect Mcu Channel Host Error.");
    resetStatus();

}

void McuChannel::onJsonText(const std::string & text,const Connection::Ptr& conn){
    std::lock_guard<std::recursive_mutex> lock(this->rmutex_);

    last_heart_time_ = std::time(NULL);

    Application::instance()->getLogger().debug("<< Recv Buffer From McuProxy: " + text);
    MessagePayload::Ptr message;
    if (listener_) {
//			 message = parseSensorMessage(line.c_str());
//        Application::instance()->getLogger().debug("parse sensor message:" + line);
        message = MessagePayload::parse(text);
        if (message && listener_) {
            listener_->onMessage(message, NULL);
        }
    }


//    std::vector<std::string> lines;
//
//    const char * data = text.c_str();
//    size_t size = text.size();
//
//    buffer_ = std::string(data, size);
//    Application::instance()->getLogger().debug("<< buffer: " + buffer_);
//
//    databuf_.resize(databuf_.size() + size);
//    memcpy(&databuf_[databuf_.size() - size],data,size);
//
//    lines = data_split();
//
//
//    MessagePayload::Ptr message;
//    for (auto &line : lines) {
//        if (listener_) {
//            Application::instance()->getLogger().debug("parse sensor message:" + line);
//            message = MessagePayload::parse(line);
//            if (message && listener_) {
//                listener_->onMessage(message, NULL);
//            }
//        }
//    }


}


std::vector<std::string> McuChannel::data_split(){
    std::vector<std::string> lines;
    while(true) {
        auto itr = std::find(databuf_.begin(), databuf_.end(), SP);
        if (itr == databuf_.end()) {
            break;
        }
        std::string text(databuf_.begin(),itr) ;
        databuf_.erase(databuf_.begin(),itr+1);
        lines.push_back(text);
    }
    return lines;
}

void McuChannel::setListener(ISensorListener *listener) {
    listener_ = listener;
}

// 发送下行串口消息
void McuChannel::sendData(const char *data, size_t size) {
    std::lock_guard<std::recursive_mutex> lock(this->rmutex_);
    if(conn_.get()){
        conn_->send(data,size);
    }
    std::string text(data,size);
    Application::instance()->getLogger().debug("SendTcpData To McuProxy:"+text);
}

void McuChannel::sendMessage(const std::shared_ptr<MessagePayload> &message) {
    if (message) {
        std::string text = message->marshall();
        sendData(text.c_str(), text.size());
        sendData(std::string(1,SP).c_str(), 1);
    }
}
