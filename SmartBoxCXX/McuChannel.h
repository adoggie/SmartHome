//
// Created by scott on 2019-06-07.
//

#ifndef SMARTBOX_MCUCHANNEL_H
#define SMARTBOX_MCUCHANNEL_H


#include "base.h"
#include "service.h"
#include "connection.h"
#include "watchdog.h"
#include "message.h"
#include "connection.h"
#include "version.h"
#include "sensor.h"

#include <jsoncpp/json/json.h>
#include <boost/asio.hpp>

// tcp 连接到 设备管理代理对象




class McuChannel: public Service,IConnectionListener, public std::enable_shared_from_this<McuChannel> {

public:
    McuChannel(){}
    typedef std::shared_ptr<McuChannel> Ptr;
    bool init(const Config& props);
    bool open();
    void close();

    void sendData(const char *data, size_t size);    // 写入数据
    void sendMessage(const std::shared_ptr<MessagePayload>& message);
    void sendSeperator(); //发送包分割符
    void setListener(ISensorListener *listener);

    void run(){}
    void resetStatus();
    std::vector<std::string> data_split();
protected:
    void workTimedTask();
    void onConnected(const Connection::Ptr& conn);
    void onDisconnected(const Connection::Ptr& conn);
    void onData(boost::asio::streambuf& buffer,const Connection::Ptr& conn);
    void onJsonText(const std::string & text,const Connection::Ptr& conn);
    void onConnectError(const Connection::Ptr& conn,ConnectionError error);

    void reqUpdateSensorStatus();   //请求所有sensor上报一次
protected:
    Config 		cfgs_;
    std::recursive_mutex  rmutex_;

    std::shared_ptr<boost::asio::steady_timer> timer_;
    int         check_timer_interval_;
    bool        data_inited_ ;
    std::time_t     last_check_time_ = 0;
    std::time_t     last_heart_time_ = 0;

    int         mcu_channel_port_ = 8001 ; //
    std::string     mcu_channel_host_ ; // mcu 代理服务地址

    Connection::Ptr conn_;                  //到平台服务器连接
    std::time_t 	boot_time_ = 0;

    std::string buffer_;
    std::vector< std::uint8_t > databuf_;
    ISensorListener *listener_;
};


#endif //SMARTBOX_MCUCHANNEL_H
