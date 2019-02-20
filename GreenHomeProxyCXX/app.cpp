//
// Created by bin zhang on 2019/1/6.
//

#include "app.h"
#include <boost/program_options.hpp>

namespace  bpo = boost::program_options;

//bpo::variables_map vm;

std::shared_ptr<Application>& Application::instance(){
	static std::shared_ptr<Application> handle ;
	if(!handle.get()){
		handle = std::make_shared<Application>();
	}
	return handle;
}

///  options parse to reference:
///  https://blog.csdn.net/morning_color/article/details/50241987

Application&  Application::init(int argc , char ** argvs){
	cfgs_.load("settings.txt");
//	Logger::HandlerPtr handle =
	logger_.addHandler( std::make_shared<LogStdoutHandler>());
	
	
	
	bpo::options_description opts("all options");
	bpo::variables_map vm;
	
	//步骤二: 为选项描述器增加选项
	//其参数依次为: key, value的类型，该选项的描述
	opts.add_options()
			("id", bpo::value<std::string>(), "the unique id of smartbox.")
			("logfile", bpo::value<std::string>(), "the running info into log file.")
			("help", "more usage information..");
	
	//步骤三: 先对命令行输入的参数做解析,而后将其存入选项存储器
	//如果输入了未定义的选项，程序会抛出异常，所以对解析代码要用try-catch块包围
	try {
		bpo::store(bpo::parse_command_line(argc, argvs, opts), vm);
		if (vm.count("id")) {
			cfgs_.set_string("id", vm["id"].as<std::string>());
		}
		if (vm.count("logfile")) {
			cfgs_.set_string("log.file", vm["logfile"].as<std::string>());
		}
		
	}catch(...){
		this->getLogger().error("Program Options Parse Failed.");
	}
	
	logger_.addHandler( std::make_shared<LogFileHandler>(cfgs_.get_string("log.file")));
	
	return *this;
}


Logger& Application::getLogger(){
	return logger_;
}

void Application::run(){
	
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

void Application::processOptions(int argc , char ** argvs) {

}

int main(int argc , char ** argvs){
	Application::instance()->init(argc,argvs).run();
}

