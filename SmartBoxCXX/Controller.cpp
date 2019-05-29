//
// Created by bin zhang on 2019/1/11.
//

#include "Controller.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mcu.h"
#include "http.h"
#include "app.h"
#include "utils.h"
#include "version.h"
#include "base64_.h"
#include "tcpchannel.h"

bool Controller::init(const Config& props){
	settings_.login_inited = false;

	cfgs_ = props;
	if(props.get_int("watchdog.enable",0)) {
		watchdog_.init(props);
	}
	resetStatus();

	McuController::instance()->init(props);
	HttpService::instance()->init(props);
	TcpCommandChannelManager::instance()->init(props);

	check_timer_interval_ = cfgs_.get_int("controller.check_timer",5);

	timer_ = std::make_shared<boost::asio::steady_timer>(io_service_);
	timer_->expires_after(std::chrono::seconds( check_timer_interval_));
	timer_->async_wait(std::bind(&Controller::workTimedTask, this));

	return true;
}

bool Controller::open(){
	if(cfgs_.get_int("watchdog.enable",0)) {
		watchdog_.open();
	}

	net_check_interval_ = cfgs_.get_int("net_check_interval",60);

	McuController::instance()->open();
	HttpService::instance()->open();
	TcpCommandChannelManager::instance()->open();

//	reportEvent( std::make_shared<Event_SystemStart>());

	return true;
}


void Controller::close(){
	watchdog_.close();
	HttpService::instance()->close();
}

void Controller::run(){
	io_service_.run();
}


Json::Value Controller::getStatusInfo(){
	/*
	 { device_id,device_type,host_ver,mcu_ver,boot_time,
	 	sensors:[
	 		{sensor_type,sensor_id,f1:x,f2:x,f3:x}
	 	]
	 }
	 */
	// todo. 需要完成
	Json::Value value;
//	value[""]
	return value;
}

void Controller::resetStatus(){
	std::lock_guard<std::recursive_mutex> lock(rmutex_);

	settings_.login_inited = false;
	if(conn_){
		conn_->close();
		conn_.reset();
	}
}
// 定时工作任务
void Controller::workTimedTask(){
	std::lock_guard<std::recursive_mutex> lock(rmutex_);

	httpInitData();

	if(!conn_ && settings_.login_inited){
		// 准备发起连接到服务器
		conn_ = std::make_shared<Connection>(get_io_service());
		conn_->setListener(this);
		boost::asio::ip::address address = boost::asio::ip::make_address(settings_.comm_server_ip);
		boost::asio::ip::tcp::endpoint ep(address,(std::uint32_t )settings_.comm_server_port);
		std::stringstream ss;
		ss<<"Connect to server:" << settings_.comm_server_ip << ":" << settings_.comm_server_port;
		Application::instance()->getLogger().debug(ss.str());
		conn_->startConnect(ep);
		last_heart_time_ = std::time(NULL);
	}

	// 如果超时接收不到来自服务器的心跳包，则关闭连接，再次进行登录
	if( std::time(NULL) - last_heart_time_ > 60*1){
		resetStatus();
//		last_check_time_ = std::time(NULL);
//		check_net_reachable();
	}

	if(conn_){
		//发送心跳
		MessageHeartBeat hb;
		hb.device_id = getDeviceUniqueID();
		conn_->send(hb.marshall());
	}

	timer_->expires_after(std::chrono::seconds( check_timer_interval_));
	timer_->async_wait(std::bind(&Controller::workTimedTask, this));
}


void Controller::check_net_reachable() {
//	{
//		std::string address = cfgs_.get_string("propserver_url", "http://127.0.0.1:8090");
//		std::string url = (boost::format("%s/propserver/api/ping") % address.c_str()).str();
//		PropertyStringMap vars;
//		HttpService::instance()->http_request(url, PropertyStringMap(), vars, (void *) "check_propserver");
//	}

}


std::string Controller::getDeviceUniqueID(){
	// todo. 提供获取设备硬件编码的接口
	std::string uid;
	uid = utils::getDeviceUniqueId();
	if(uid.size() == 0) {
		uid = cfgs_.get_string("id");
	}
	return uid;
}

// 设置设备运行参数值
void Controller::setParameterValues(const PropertyStringMap& params){
	std::string value;
	if(params.find("login_server_url")!= params.end()){
		auto url = boost::lexical_cast<std::string>(params.at("login_server_url"));
		settings_.login_server_url = url;
		saveUserSettings();
	}
	if(params.find("save")!= params.end()){
		saveUserSettings();
	}
	// 设备重启
	if(params.find("reboot")!= params.end()){
		this->reboot();
	}
	// 指定 网卡 dhcp获取ip  nic_dhcp=eth0 令eth0 动态获取
	if(params.find("nic_dhcp")!= params.end()){
		this->reboot();
	}
	// 设置网络接口ip地址
	if(params.find("nic_ip_eth0")!= params.end()){
		auto ip = boost::lexical_cast<std::string>(params.at("nic_ip_eth0"));
		utils::setNicIpAddress("eth0",ip);
	}

	if(params.find("nic_ip_eth1")!= params.end()){
		auto ip = boost::lexical_cast<std::string>(params.at("nic_ip_eth0"));
		utils::setNicIpAddress("eth1",ip);
	}
}

void Controller::setParameterValues(const std::string& name, const std::string&  value, const std::string& module){
    if(name == "login_server_url"){
        auto url = boost::lexical_cast<std::string>(value);
        settings_.login_server_url = url;
        saveUserSettings();
    }
    if( name == "save"){
        saveUserSettings();
    }
    // 设备重启
    if( name == "reboot"){
        this->reboot();
    }
    // 指定 网卡 dhcp获取ip  nic_dhcp=eth0 令eth0 动态获取
    if(  name == "nic_dhcp" ){
        this->reboot();
    }
    // 设置网络接口ip地址
    if( name == "nic_ip_eth0"){
        auto ip = boost::lexical_cast<std::string>( value);
        utils::setNicIpAddress("eth0",ip);
    }

    if( name == "nic_ip_eth1"){
        auto ip = boost::lexical_cast<std::string>( value );
        utils::setNicIpAddress("eth1",ip);
    }
}

void Controller::loadUserSettings(){

}

void Controller::saveUserSettings(){
	Config user;
	user.set_string("login_server_url", settings_.login_server_url);
	user.save(SETTINGS_USER_FILE);
}

void Controller::reboot(){
	::system("reboot");
}


// 未初始化则进行初始化，需要定时器进行驱动
void Controller::httpInitData(){
	if( settings_.login_inited ) {
		return ;
	}
	// 未登录则进行登录
//	data_inited_ = true; // todo .for debug & test , remove later.
	std::string device_id = getDeviceUniqueID();
	std::string address = cfgs_.get_string("login_server_url","http://127.0.0.1:8091");

	std::string device_type = "1";
	std::string ver = VERSION;
	std::string time = boost::lexical_cast<std::string>( std::time(NULL) );
	std::string key = cfgs_.get_string("secret_key","12345678");
	std::string text = "id"+ device_id + "time"+ time + "type" + device_type + "ver" + ver ;
	std::string sign = utils::generateSignature(key,text);

	std::string url = (boost::format("%s?id=%s&type=%s&ver=%s&time=%s&sign=%s")
						%address.c_str()% device_id.c_str()%device_type.c_str()
					   %ver.c_str()%time.c_str()%sign.c_str() ).str();

	PropertyStringMap vars;
	HttpService::instance()->http_request(url,PropertyStringMap(),vars,(void*)"login_req"); // 登录返回接入服务器信息
}


//http client 请求返回数据处理
void Controller::onHttpResult(const std::string& request_name,const Json::Value & root){

	Json::Value result = root.get("result",Json::Value());

	if( request_name == "login_req"){
//		onInitData(result);
		onLoginResponse(result);
	}
}

// 登录返回
// token , server_ip , server_port
void Controller::onLoginResponse(const Json::Value& result){
	std::lock_guard<std::recursive_mutex> lock(rmutex_);

	if( result.isNull()){
		return;
	}
	//登录成功
	settings_.login_inited = true;
	settings_.login_time = std::time(NULL);
	settings_.comm_server_ip = result["server_ip"].asString();
	settings_.comm_server_port =(std::uint16_t) result["server_port"].asUInt();
	settings_.token = result["token"].asString();

}
// 获取家庭网络地址 eth0
std::string Controller::getInnerIP(){
	std::string nic  = cfgs_.get_string("nic_1","eth0");
	std::string ip;
	ip = utils::getIpAddress(nic);
	return ip;
}

//设备小区网络地址 eth1
std::string Controller::getOuterIP(){
	std::string nic  = cfgs_.get_string("nic_2","eth1");
	std::string ip;
	ip = utils::getIpAddress(nic);
	return ip;
}


void Controller::onConnected(const Connection::Ptr& conn){
	std::lock_guard<std::recursive_mutex> lock(this->rmutex_);

	std::shared_ptr<MessageLogin> login_req = std::make_shared<MessageLogin> ();
	login_req->device_id = getDeviceUniqueID();
	login_req->token = settings_.token;
	// 呼叫连接建立，发送登录消息包
	conn->send( login_req->marshall());

	// 发送 profile 到平台

	std::string profile = Application::instance()->getConfig().get_string("profile");
	std::ifstream ifs;
	ifs.open(profile);
	if( ifs.is_open() ){
		ifs.seekg(0, std::ios::end);
		int length = ifs.tellg();
		ifs.seekg(0, std::ios::beg);
		char * buf = new char[length];
		ifs.read(buf,length);
		ifs.close();

		std::string str_in(buf,length),str_out;
		bool succ = Base64::Encode(str_in,&str_out);
		if(succ){
			std::shared_ptr<MessageDeviceStatus> status = std::make_shared<MessageDeviceStatus>();
			status->params["profile"] = str_out;
			status->params["encode"] = "base64";
			conn->send(status->marshall());
		}

		delete [] buf;
	}

//	live_time_outside_ = std::time(NULL);
}

//外部连接丢失
void Controller::onDisconnected(const Connection::Ptr& conn){
	std::lock_guard<std::recursive_mutex> lock(this->rmutex_);
	Application::instance()->getLogger().debug("Connection Disconnected..");
	resetStatus();

//	live_time_inside_ = live_time_outside_ = 0;
}

void Controller::onData( boost::asio::streambuf& buffer,const Connection::Ptr& conn){

}

//对外连接失败
void Controller::onConnectError(const Connection::Ptr& conn,ConnectionError error){
	std::lock_guard<std::recursive_mutex> lock(this->rmutex_);
	resetStatus();

}

void Controller::onJsonText(const std::string & text,const Connection::Ptr& conn){
	std::lock_guard<std::recursive_mutex> lock(this->rmutex_);

	Message::Ptr message = MessageJsonParser::parse(text.c_str(),text.size());
	if(!message){
		return ;
	}
	std::shared_ptr<MessagePayload> payload;
	Application::instance()->getLogger().debug("onJsonText : "+ message->name());
	{
		std::shared_ptr<MessageLoginResp> msg = std::dynamic_pointer_cast<MessageLoginResp>(message);
		if (msg) {
			// 登录反馈
			if(msg->error){
				Application::instance()->getLogger().error("login error:" + boost::lexical_cast<std::string>(msg->error));
				resetStatus();
			}
			return;
		}
	}


	{ //查询端点设备状态
		std::shared_ptr<MessageSensorStatusQuery> msg = std::dynamic_pointer_cast<MessageSensorStatusQuery>(message);
		if(msg){
			payload = msg->asPayload();
			McuController::instance()->sendMessage(payload);
			return;
		}
	}

	{ // 设置端点设备运行参数
		std::shared_ptr<MessageSensorValueSet> msg = std::dynamic_pointer_cast<MessageSensorValueSet>(message);
		if(msg) {
			payload = msg->asPayload();
			McuController::instance()->sendMessage(payload);
			return;
		}
	}


	{ // 设备运行状态查询
		std::shared_ptr<MessageDeviceStatusQuery> msg = std::dynamic_pointer_cast<MessageDeviceStatusQuery>(message);
		if(msg) {
			payload = msg->asPayload();
			McuController::instance()->sendMessage(payload);
			return;
		}
	}

	{ //设备参数设置
		std::shared_ptr<MessageDeviceValueSet> msg = std::dynamic_pointer_cast<MessageDeviceValueSet>(message);
		if(msg) {
			payload = msg->asPayload();
			McuController::instance()->sendMessage(payload);
			return;
		}
	}

	{ //心跳
		std::shared_ptr<MessageHeartBeat> msg = std::dynamic_pointer_cast<MessageHeartBeat>(message);
		if(msg) {
			last_heart_time_ = std::time(NULL);
			return;
		}
	}
}

// 发送到云端
void Controller::onTraverseUpMessage(const std::shared_ptr<MessageTraverseUp> message){
    Application::instance()->getLogger().debug("onTraverseUpMessage :" + message->marshall());

	std::lock_guard<std::recursive_mutex> lock(rmutex_);
	message->device_id = getDeviceUniqueID();
	if(conn_){
		conn_->send(message->marshall());
	}
	// 发送给连接的app
	TcpCommandChannelManager::instance()->postMessage(message);
}

void Controller::onTraverseDownMessage(const std::shared_ptr<MessageTraverseDown> message){

}
