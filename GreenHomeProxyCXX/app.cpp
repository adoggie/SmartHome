//
// Created by bin zhang on 2019/1/6.
//

#include "app.h"
#include "Controller.h"
#include <boost/program_options.hpp>
namespace  bpo = boost::program_options;

std::shared_ptr<Application>& Application::instance(){
	static std::shared_ptr<Application> handle ;
	if(!handle.get()){
		handle = std::make_shared<Application>();
	}
	return handle;
}

///

Application&  Application::init( int argc , char ** argv ){
	inited_ = false;

	bpo::options_description opts("all options");
	bpo::variables_map vm;

	opts.add_options()
			("id", bpo::value<std::string>(), "device unique id specified")
			("help", "--- green-agent help --- ");
	try{
		bpo::store(bpo::parse_command_line(argc, argv, opts), vm);
	}
	catch(...){
		std::cout << "输入的参数中存在未定义的选项！\n";
		return *this;
	}

	if(vm.count("id") == 0 ) {
		std::cout << " Device id needed." << std::endl;
		return *this;
	}

	std::string device_id = vm["id"].as<std::string>();


	cfgs_.load("/var/green/settings.txt");

	// 更新用户自定义的参数
//	Config user;
//	user.load("settings.user");
//	cfgs_.update(user);
//	cfgs_.set_string("device_id",device_id);

	std::string datapath = cfgs_.get_string("datapath","/var/green/data");
	datapath+='/'+device_id;
	cfgs_.set_string("datapath",datapath);
	cfgs_.set_string("device_id", device_id);
	std::string logfile = datapath + "/logs.txt";

	logger_.setLevel(Logger::DEBUG);
	logger_.addHandler( std::make_shared<LogStdoutHandler>());
	logger_.addHandler( std::make_shared<LogFileHandler>(logfile));

	//开启调试输出
//	if( cfgs_.get_string("debug.log.udp.enable") == "true") {
//		std::string host = cfgs_.get_string("debug.log.udp.host", "127.0.0.1");
//		uint16_t port = cfgs_.get_int("debug.log.udp.port", 9906);
//		logger_.addHandler(std::make_shared<LogUdpHandler>(host, port));
//	}

	Controller::instance()->init(cfgs_);
	Controller::instance()->open();

	inited_ = true;
	return *this;
}


Logger& Application::getLogger(){
	return logger_;
}

void Application::run(){
    if( inited_ == false){
        return;
    }
	Controller::instance()->run();
	wait_for_shutdown();
}

void Application::stop(){
	cv_.notify_one();
}

void Application::addService(std::shared_ptr<Service>& service ){
	services_.push_back(service);
}

Config& Application::getConfig(){
	return cfgs_;
}

void Application::wait_for_shutdown(){
	getLogger().info(name() + " started..");
	
	std::unique_lock<std::mutex> lk(mutex_);
	cv_.wait(lk);
}

std::string Application::name(){
	return cfgs_.get_string("application.name","Application");
}

int main(int argc , char ** argv){
	Application::instance()->init(argc, argv).run(  );
}

