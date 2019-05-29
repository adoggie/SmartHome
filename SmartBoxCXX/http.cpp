
#include "http.h"

#include "mongoose.h"
#include <thread>
#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>
#include <jsoncpp/json/json.h>

#include "Controller.h"
#include "app.h"
#include "error.h"
#include "md5.hpp"
#include "base64_.h"
#include "mcu.h"


// mongoose help
// https://cesanta.com/docs/overview/intro.html
// https://github.com/cesanta/mongoose/blob/master/examples/simple_crawler/simple_crawler.c
// https://github.com/Gregwar/mongoose-cpp


/*
 提供接口：
 设备离线或在线
 1. 家庭网络内App发起的对智能设备的控制和状态查询
 2. Roki设备发送的基于ssdp服务的设备控制接口
 */
static const char *s_http_port = "8000";
static struct mg_serve_http_opts s_http_server_opts;
struct mg_mgr mgr;
//struct mg_connection *nc;
struct mg_bind_opts bind_opts;

std::string http_get_var(struct http_message *hm,const std::string& name,const std::string& def=""){
	char buf[1200];
	int ret;

	std::string val;
	ret = mg_get_http_var(&hm->body, name.c_str(), buf, sizeof(buf));
	if(ret > 0 ){
		val = buf;
	}else{
	    val = def;
	}
	return val;
}

std::string http_get_query_var(struct http_message *hm,const std::string& name,const std::string& def=""){
    char buf[1200];
    int ret;

    std::string val;
    ret = mg_get_http_var(&hm->query_string, name.c_str(), buf, sizeof(buf));
    if(ret > 0 ){
        val = buf;
    }else{
        val = def;
    }
    return val;
}


HttpHeaders_t defaultResponseHeaders(){
	return {
			{"Content-Type","application/json"},
			{"Transfer-Encoding","chunked"}
	};
}

Json::Value defaultResponseJsonData(int status=HTTP_JSON_RESULT_STATUS_OK,int errcode = Error_NoError,const char* errmsg=""){
	Json::Value data;
	data["status"] = status;
	data["errcode"] = errcode;
	data["errmsg"] = errmsg;
	if(errmsg == std::string("")){
		data["errmsg"] =  ErrorDefs.at(errcode);
	}
	return data;
}


Json::Value errorResponseJsonData(int errcode = Error_NoError,const char* errmsg=""){
	Json::Value data;
	data["status"] = HTTP_JSON_RESULT_STATUS_ERROR;
	data["errcode"] = errcode;
	data["errmsg"] = errmsg;
	if(errmsg == std::string("")){
		data["errmsg"] =  ErrorDefs.at(errcode);
	}
	return data;
}


void send_http_response(struct mg_connection *nc,const std::string& text,const HttpHeaders_t& headers){
//	mg_printf(nc, "%s", "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n");
	mg_printf(nc, "%s", "HTTP/1.1 200 OK\r\n");
	
	
	for(auto p:headers) {
		mg_printf(nc, "%s: %s\r\n", p.first.c_str(),p.second.c_str());
	}
	mg_printf(nc, "%s", "\r\n");
	
	mg_send_http_chunk(nc, text.c_str(), text.size());
	mg_send_http_chunk(nc, "", 0);
}


void send_http_response_error(struct mg_connection *nc,int errcode = Error_NoError,const char* errmsg="") {
    Json::Value data = errorResponseJsonData(errcode,errmsg);
    std::string text = data.toStyledString();
    send_http_response(nc, text, defaultResponseHeaders());
}

void send_http_response_okay(struct mg_connection *nc,int errcode = Error_NoError,const char* errmsg="") {
    Json::Value data = defaultResponseJsonData();
    std::string text = data.toStyledString();
    send_http_response(nc, text, defaultResponseHeaders());
}

void send_http_response_result(Json::Value result,struct mg_connection *nc,int errcode = Error_NoError,const char* errmsg="") {
    Json::Value data = defaultResponseJsonData();
    data["result"] = result;
    std::string text = data.toStyledString();
    send_http_response(nc, text, defaultResponseHeaders());
}


//查询设备运行状态
void HttpService::handle_status_query(struct mg_connection *nc, struct http_message *hm ){
	Json::Value data = defaultResponseJsonData();
	data["result"] = Controller::instance()->getStatusInfo();
	std::string text = data.toStyledString();
	send_http_response(nc,text,defaultResponseHeaders());
}

// 删除注册的室内机
//void HttpService::handle_innerdevice_remove(struct mg_connection *nc, struct http_message *hm ){
//	std::string token ;
//	struct mg_str* str = mg_get_http_header(hm,"token");
//}

/**
 * check_auth
 * @param hm
 * @param code
 * @return
 * @remark token的尾部32字节是签名校验码(md5),
 * 	if md5(secret_key,token[0:-32]) == token[-32:]
 * 		ok(..)
 * 	else
 * 	    error(..)
 *
 *  token 可携带设备的相关信息，采用base64编码
 *
 *  物业中心发起对室内机的查询请求，token是固定值
 *
 *
 */
bool HttpService::check_auth(struct mg_connection *nc,struct http_message *hm,const std::string& code ){
	std::string token ;
//	struct mg_str* str = mg_get_http_header(hm,"token");
    token = http_get_var(hm,"token");
	if ( cfgs_.get_string("advance_access_token") == token ){
	    return true ;
	}
    return true;

    Json::Value data = errorResponseJsonData(Error_TokenInvalid);
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());

	return  false;
}


// url = /smartbox/api/sensor/params
void HttpService::handle_sensor_params_set(struct mg_connection *nc, struct http_message *hm ){
//    if( check_auth(nc,hm) == false){
//        return;
//    }
    PropertyStringMap values;
    std::vector< std::string > names = {"sensor_type","sensor_id","name", "value"};
    std::string sensor_type = http_get_var(hm,"sensor_type");
    std::string sensor_id = http_get_var(hm,"sensor_id");
    std::string param_name = http_get_var(hm,"name");
    std::string param_value = http_get_var(hm,"value");

    McuController::instance()->setSensorValue(sensor_id,sensor_type,param_name,param_value);
    send_http_response_okay(nc);
}

// 查询指定端点设备的状态值
// url : /smartbox/api/sensor/status
void HttpService::handle_sensor_status_query(struct mg_connection *nc, struct http_message *hm ){
    PropertyStringMap values;
    std::string sensor_type = http_get_query_var(hm,"sensor_type");
    std::string sensor_id = http_get_query_var(hm,"sensor_id");
    values = McuController::instance()->getSensorStatus(sensor_id,sensor_type);

    Json::Value result;
    result["sensor_id"] = sensor_id;
    result["sensor_type"] = sensor_type;
    for( auto p:values){
        result[p.first] = p.second;
    }

    Json::Value data = defaultResponseJsonData();
    data["result"] = result;
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

// 上报 端设备状态 ( 测试 )
void HttpService::handle_sensor_status_upload(struct mg_connection *nc, struct http_message *hm ){
    PropertyStringMap values;
    std::string sensor_type = http_get_var(hm,"sensor_type");
    std::string sensor_id = http_get_var(hm,"sensor_id");
    std::string name = http_get_var(hm,"name");
    std::string value = http_get_var(hm,"value");

    std::shared_ptr<MessageSensorStatus> status = std::make_shared<MessageSensorStatus>();
    status->sensor_id = boost::lexical_cast<int>(sensor_id);
    status->sensor_type = boost::lexical_cast<int>(sensor_type);
    status->params[name] = value;
    Controller::instance()->onTraverseUpMessage(status);

    Json::Value data = defaultResponseJsonData();
//    data["result"] = result;
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

//获得设备的profile定义
void HttpService::handle_profile_get(struct mg_connection *nc, struct http_message *hm ){
    std::string profile = Application::instance()->getConfig().get_string("profile");
    std::ifstream ifs;
    Json::Value data = defaultResponseJsonData();

    ifs.open(profile);
    if( ifs.is_open() ){
        ifs.seekg(0, std::ios::end);
        int length = ifs.tellg();

        ifs.seekg(0, std::ios::beg);
        char * buf = new char[length+1];
        buf[length] = 0;
        ifs.read(buf,length);

        Json::Reader reader;
        Json::Value result;
        if (reader.parse(buf, result)){
            data["result"] = result;
        }
        delete [] buf;
    }


    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

// 设置设备运行参数
// 修改密码，保存到 settings.user 文件
void HttpService::handle_params_set(struct mg_connection *nc, struct http_message *hm ){
    if( check_auth(nc,hm) == false){
        return;
    }
    PropertyStringMap values;
//    std::vector< std::string > names = {"watchdog_enable","alarm_enable","reboot",
//                                        "nic_dhcp","save","nic_ip_eth0","nic_ip_eth1",
//                                        "login_server_url"
//                                        };
    std::vector< std::string > names = {"id","name","value","module"};

//    for( auto _ : names){
//        std::string value = http_get_var(hm,_);
//        if(value.length()){
//            values[_] = value;
//        }
//    }
    std::string name , value ,module;
    name = http_get_var(hm, "name");
    value = http_get_var(hm, "value");
    module = http_get_var(hm, "module");

    Controller::instance()->setParameterValues(name,value,module);
//    Controller::instance()->setParameterValues(values);

    send_http_response_okay(nc);
}

void HttpService::ev_handler(struct mg_connection *nc, int ev, void *ev_data) {
	struct http_message *hm = (struct http_message *) ev_data;
	HttpService* http = HttpService::instance().get();
    std::string method ;
    std::string url;

    try {
        switch (ev) {
            case MG_EV_HTTP_REQUEST:
                method = std::string(hm->method.p,hm->method.len) ;
                boost::to_lower(method);
                url =std::string (hm->uri.p,hm->uri.len);
                Application::instance()->getLogger().debug(url);
                if (mg_vcmp(&hm->uri, "/smartbox/discover") == 0) {
//				http->handle_innerdevice_discover(nc, hm); /* Handle RESTful call */

                } else if (mg_vcmp(&hm->uri, "/api/smartbox/status") == 0) { // 设备状态查询
                    http->handle_status_query(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/api/smartbox/params") == 0) { // 设备参数设置
                    http->handle_params_set(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/api/smartbox/sensor/params") == 0) { // 设备参数查询
                    http->handle_sensor_params_set(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/api/smartbox/sensor/status") == 0) { // 设备参数设置
                    http->handle_sensor_status_query(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/api/smartbox/profile") == 0) { // 设备profile 查询
                    http->handle_profile_get(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/api/smartbox/sensor/status/upload") == 0) { // 设备profile 查询
                    http->handle_sensor_status_upload(nc, hm);
                } else {
                    mg_serve_http(nc, hm, s_http_server_opts); /* Serve static content */
                }
                break;
            default:
                break;
        }
    }catch (boost::bad_lexical_cast& e){
        send_http_response_error(nc,Error_ParameterInvalid);
    }
}

void HttpService::thread_run() {
	
	
	running_ = true;
	while( running_ ){
		mg_mgr_poll(&mgr, 1000);
	}
	mg_mgr_free(&mgr);
	
}

bool  HttpService::init(const Config& cfgs){
	cfgs_ = cfgs;
	return true;
}

bool HttpService::open(){
	
	int i;
	char *cp;
	const char *err_str;
    struct mg_connection *nc;
	mg_mgr_init(&mgr, NULL);
	s_http_server_opts.document_root = "/tmp/smartbox/http";
	std::string http_port  = cfgs_.get_string("http.port","8000");
	
//	std::function< void (struct mg_connection *, int , void *) >  fx =std::bind( &HttpService::ev_handler,_1,_2,_3);
//	auto  fx =std::bind( &HttpService::ev_handler,_1,_2,_3);
	
//
//	nc = mg_bind_opt(&mgr, s_http_port,std::bind(&HttpService::ev_handler,this,_1,_2,_3), bind_opts);
	nc = mg_bind_opt(&mgr, http_port.c_str(),HttpService::ev_handler, bind_opts);
//	nc = mg_bind_opt(&mgr, s_http_port,(mg_event_handler_t)fx, bind_opts);
	if (nc == NULL) {
		fprintf(stderr, "Error starting server on port %s: %s\n", http_port.c_str(),
		        *bind_opts.error_string);
		return false;
	}
	Application::instance()->getLogger().info("starting http server on port :" + http_port);
	mg_set_protocol_http_websocket(nc);
	s_http_server_opts.enable_directory_listing = "yes";
	
	printf("Starting RESTful server on port %s, serving %s\n", http_port.c_str(),
	       s_http_server_opts.document_root);
	thread_ = std::make_shared<std::thread>( std::bind(&HttpService::thread_run,this));
	
	return true;
}

void HttpService::close(){
	running_ = false;
	thread_->join();
}

void HttpService::run() {
//	thread_->join();
}

// 向外 http 连接请求返回处理入口
void ev_connect_handler(struct mg_connection *nc, int ev, void *ev_data) {

    std::string name = (char*) nc->user_data;
    HttpService* http = HttpService::instance().get();

    if (ev == MG_EV_HTTP_REPLY) { // 服务器返回
        struct http_message *hm = (struct http_message *)ev_data;
        nc->flags |= MG_F_CLOSE_IMMEDIATELY;


        Json::Reader reader;
        Json::Value root;
        std::string json(hm->body.p,hm->body.len);
        Application::instance()->getLogger().debug("Http Response:" + json);
        if (reader.parse(json, root)){
            if( root.get("status",Json::Value("0")).asInt() != 0){
                // error
                return ;
            }
        }else{
            Application::instance()->getLogger().debug("Http Response Data Parse Error");
            return ;
        }

        Controller::instance()->onHttpResult(name,root);

    } else if (ev == MG_EV_CLOSE) {
//        exit_flag = 1;
    };

}

// 设备上线查询运行参数
void HttpService::handle_resp_init_data(Json::Value& root ){

}

void HttpService::http_request(const std::string& url, const PropertyStringMap& headers, const PropertyStringMap& vars,
                  void* user_data){
    struct mg_connection *nc;

    //处理http header
    std::string head_text ;
    for(auto p:headers) {
        boost::format fmt("%s: %s\r\n");
        fmt % p.first.c_str() % p.second.c_str();
        head_text +=  fmt.str();
    }
    if(head_text.length() == 0){
        head_text = "Content-Type: application/x-www-form-urlencoded\r\n";
    }

    // 处理post 参数
    std::string var_text ;
    for(auto p:vars) {
        std::string key ,value;
        key = p.first;
        value = p.second;
        mg_str k = mg_mk_str(key.c_str());
        mg_str v = mg_mk_str(value.c_str());

        k = mg_url_encode(k);
        v = mg_url_encode(v);
        key = std::string(k.p,k.len);
        value = std::string(v.p,v.len);

        free((void*)k.p);
        free((void*)v.p);

        if( var_text.length()){
            var_text +=  "&";
        }
        var_text += key + "=" + value;
    }
    if( var_text.length()) {
        nc = mg_connect_http(&mgr, ev_connect_handler,url.c_str(), head_text.c_str(), var_text.c_str());
    }else{
        nc = mg_connect_http(&mgr, ev_connect_handler,url.c_str(), head_text.c_str(), NULL);
    }
    nc->user_data = user_data;

}

