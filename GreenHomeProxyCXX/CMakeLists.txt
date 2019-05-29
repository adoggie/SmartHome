cmake_minimum_required(VERSION 2.8)
project(GreenHomeProxy)

set(CMAKE_CXX_STANDARD 11)
add_definitions( -D_MACOS )
add_compile_options(-Wwrite-strings)
include_directories(/usr/local/include)
link_directories("/usr/local/Cellar/boost/1.66.0/lib" "/usr/local/lib" )
#link_directories(/usr/local/lib)
link_libraries( boost_system boost_program_options jsoncpp pthread uspsdk hiredis redis++ )
add_executable(GreenHomeProxy app.cpp app.h config.cpp config.h
        service.cpp Controller.cpp Controller.h
        iot.cpp iot.h
        message.cpp message.h
        )



