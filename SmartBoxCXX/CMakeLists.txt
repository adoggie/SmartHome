cmake_minimum_required(VERSION 2.8)
project(SmartBox)

set(CMAKE_CXX_STANDARD 11)
add_definitions( -D_MACOS )
include_directories(/usr/local/include)
include_directories(/usr/local/include /usr/local/Cellar/boost/1.60.0_2/include)
link_directories(/usr/local/lib)
link_libraries(boost_system  jsoncpp pthread serialport )

add_executable(SmartBox Controller.cpp base64.cpp connection.cpp error.cpp logger.cpp mcu.cpp message.cpp sensor.cpp  watchdog.cpp app.cpp config.cpp crc16.c http.cpp main.cpp md5.c mongoose.c service.cpp utils.cpp
        Controller.h base.h  connection.h error.h logger.h md5.h mongoose.h service.h utils.h watchdog.h app.h base64.h config.h crc16.h http.h mcu.h message.h sensor.h stringutils.h version.h
        server.cpp codec.cpp
        tcpchannel.cpp tcpchannel.h
        McuChannel.cpp McuChannel.h)




