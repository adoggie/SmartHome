//
// Created by bin zhang on 2019/1/11.
//

#ifndef INNERPROC_INNERCONTROLLER_H
#define INNERPROC_INNERCONTROLLER_H

#include "base.h"
#include "service.h"
#include "connection.h"
#include "watchdog.h"
#include "message.h"
#include "connection.h"
#include "version.h"

#include <jsoncpp/json/json.h>
#include <boost/asio.hpp>

class Controller: public Service,IConnectionListener, public std::enable_shared_from_this<Controller> {

public:
    struct Settings{
        std::time_t         start_time;          // 启动时间
        std::time_t         login_time;
        std::string         login_server_url;              // 登录服务器url
        std::string         comm_server_ip;         // 通信服务器
        std::uint32_t       comm_server_port;          // 通信服务器端口
        std::time_t         establish_time;         //通信建立时间
        std::atomic_bool    login_inited;           // 是否已经登录
        std::string         token;                  // 接入服务的身份令牌 登录成功时返回
        Settings(){
            start_time = 0 ;
        }
    };
public:
    Controller(){}
	typedef std::shared_ptr<Controller> Ptr;
	bool init(const Config& props);
	bool open();
	void close();
	void run();
	
	static std::shared_ptr<Controller>& instance(){
		static std::shared_ptr<Controller> handle ;
		if(!handle.get()){
			handle = std::make_shared<Controller>() ;
		}
		return handle;
	}

	Json::Value getStatusInfo();
    std::string getDeviceUniqueID();


    boost::asio::io_service*  io_service(){
        return &io_service_;
    }

    void setParameterValues(const PropertyStringMap& values);
    void setParameterValues(const std::string& name, const std::string&  value, const std::string& module);

    Settings& settings() { return settings_;};

    void loadUserSettings();
    void saveUserSettings(); // 将当前配置写入 settings.user

//    void onSensorOffline(); // 防区传感器离线
    void reboot();



    std::string getInnerIP(); //家庭网络ip地址
    std::string getOuterIP();  //设备小区网络地址
//    void reportEvent(const std::shared_ptr<Event>& event);

    void onTraverseUpMessage(const std::shared_ptr<MessageTraverseUp> message); //设备上行消息
    void onTraverseDownMessage(const std::shared_ptr<MessageTraverseDown> message); //设备下行消息
    boost::asio::io_service& get_io_service(){
        return io_service_;
    }
	void onHttpResult(const std::string& request_name,const Json::Value & result);
	void onLoginResponse(const Json::Value& root); // 登录返回


private:
    void onInitData(const Json::Value& result);
    void httpInitData();
    void workTimedTask();
    void check_net_reachable();
    void resetStatus();
    void uploadProfile();
protected:
	void onConnected(const Connection::Ptr& conn);
	void onDisconnected(const Connection::Ptr& conn);
	void onData(boost::asio::streambuf& buffer,const Connection::Ptr& conn);
	void onJsonText(const std::string & text,const Connection::Ptr& conn);
	void onConnectError(const Connection::Ptr& conn,ConnectionError error);

protected:
	Config 		cfgs_;
	std::recursive_mutex  rmutex_;
    WatchDog    watchdog_;
    boost::asio::io_service io_service_;
    Settings    settings_;
    std::shared_ptr<boost::asio::steady_timer> timer_;
    int         check_timer_interval_;
    bool        data_inited_ ;
    std::time_t     last_check_time_ = 0;
    std::time_t     last_heart_time_ = 0;
    int         net_check_interval_ = 60 ; // 检测与物业和室外机网络连通性时间间隔
    Connection::Ptr conn_;                  //到平台服务器连接
    std::time_t 	boot_time_ = 0;
};


#endif //INNERPROC_INNERCONTROLLER_H
